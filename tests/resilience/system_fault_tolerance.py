#!/usr/bin/env python3
"""
System Fault Tolerance Testing Script
Kiểm tra khả năng chống chịu lỗi của hệ thống
"""

import asyncio
import docker
import json
import time
import logging
import subprocess
from datetime import datetime
from typing import List, Dict
import psutil
import requests
from kafka import KafkaProducer, KafkaConsumer, KafkaAdminClient
from kafka.admin import NewTopic
from cassandra.cluster import Cluster

# Configuration
DOCKER_COMPOSE_FILE = "docker-compose.yml"
KAFKA_BOOTSTRAP_SERVERS = ['localhost:9092']
CASSANDRA_HOSTS = ['127.0.0.1']
TEST_DURATION = 300  # 5 minutes
RECOVERY_TIMEOUT = 60  # 1 minute

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class FaultToleranceTester:
    def __init__(self):
        self.docker_client = docker.from_env()
        self.test_results = {}
        self.baseline_metrics = {}
        
    async def establish_baseline(self):
        """Thiết lập baseline metrics trước khi test"""
        logger.info("Establishing baseline metrics...")
        
        # Test Kafka throughput
        kafka_throughput = await self.measure_kafka_throughput()
        
        # Test Cassandra response time
        cassandra_latency = await self.measure_cassandra_latency()
        
        # Test system availability
        system_health = await self.check_system_health()
        
        self.baseline_metrics = {
            'kafka_throughput': kafka_throughput,
            'cassandra_latency': cassandra_latency,
            'system_health': system_health,
            'timestamp': datetime.now().isoformat()
        }
        
        logger.info(f"Baseline established: {self.baseline_metrics}")
    
    async def measure_kafka_throughput(self) -> float:
        """Đo throughput của Kafka"""
        producer = KafkaProducer(
            bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS,
            value_serializer=lambda x: json.dumps(x).encode('utf-8')
        )
        
        start_time = time.time()
        message_count = 1000
        
        for i in range(message_count):
            producer.send('test-throughput', {'id': i, 'timestamp': time.time()})
        
        producer.flush()
        producer.close()
        
        end_time = time.time()
        throughput = message_count / (end_time - start_time)
        
        logger.info(f"Kafka throughput: {throughput:.2f} messages/second")
        return throughput
    
    async def measure_cassandra_latency(self) -> float:
        """Đo latency của Cassandra"""
        try:
            cluster = Cluster(CASSANDRA_HOSTS)
            session = cluster.connect('finnhub')
            
            latencies = []
            for i in range(100):
                start_time = time.time()
                session.execute("SELECT * FROM trades LIMIT 1")
                end_time = time.time()
                latencies.append((end_time - start_time) * 1000)  # Convert to ms
            
            cluster.shutdown()
            avg_latency = sum(latencies) / len(latencies)
            
            logger.info(f"Cassandra latency: {avg_latency:.2f}ms")
            return avg_latency
            
        except Exception as e:
            logger.error(f"Error measuring Cassandra latency: {e}")
            return -1
    
    async def check_system_health(self) -> Dict:
        """Kiểm tra tình trạng sức khỏe hệ thống"""
        health = {}
        
        try:
            # Check Docker containers
            containers = self.docker_client.containers.list()
            health['running_containers'] = len(containers)
            
            # Check Kafka
            try:
                admin_client = KafkaAdminClient(bootstrap_servers=KAFKA_BOOTSTRAP_SERVERS)
                metadata = admin_client.describe_topics(['finnhub-trades'])
                health['kafka_available'] = True
            except:
                health['kafka_available'] = False
            
            # Check Cassandra
            try:
                cluster = Cluster(CASSANDRA_HOSTS)
                session = cluster.connect()
                session.execute("SELECT now() FROM system.local")
                health['cassandra_available'] = True
                cluster.shutdown()
            except:
                health['cassandra_available'] = False
            
            # System resources
            health['cpu_usage'] = psutil.cpu_percent()
            health['memory_usage'] = psutil.virtual_memory().percent
            
        except Exception as e:
            logger.error(f"Error checking system health: {e}")
        
        return health
    
    async def test_kafka_node_failure(self):
        """Test Kafka node failure"""
        logger.info("🔥 Testing Kafka node failure...")
        
        test_name = "kafka_node_failure"
        self.test_results[test_name] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # Get Kafka containers
            kafka_containers = [c for c in self.docker_client.containers.list() 
                             if 'kafka' in c.name.lower()]
            
            if not kafka_containers:
                raise Exception("No Kafka containers found")
            
            # Stop first Kafka container
            target_container = kafka_containers[0]
            container_name = target_container.name
            
            logger.info(f"Stopping Kafka container: {container_name}")
            target_container.stop()
            
            # Wait a bit for the system to detect the failure
            await asyncio.sleep(10)
            
            # Test if system can still process messages
            throughput_during_failure = await self.measure_kafka_throughput()
            
            # Check system health during failure
            health_during_failure = await self.check_system_health()
            
            # Restart the container
            logger.info(f"Restarting Kafka container: {container_name}")
            target_container.start()
            
            # Wait for recovery
            await asyncio.sleep(30)
            
            # Test recovery
            throughput_after_recovery = await self.measure_kafka_throughput()
            health_after_recovery = await self.check_system_health()
            
            # Analyze results
            degradation = (self.baseline_metrics['kafka_throughput'] - throughput_during_failure) / self.baseline_metrics['kafka_throughput'] * 100
            recovery_ratio = throughput_after_recovery / self.baseline_metrics['kafka_throughput']
            
            self.test_results[test_name].update({
                'status': 'completed',
                'container_stopped': container_name,
                'throughput_degradation': f"{degradation:.2f}%",
                'recovery_ratio': f"{recovery_ratio:.2f}",
                'health_during_failure': health_during_failure,
                'health_after_recovery': health_after_recovery,
                'passed': recovery_ratio > 0.9 and health_after_recovery['kafka_available'],
                'end_time': datetime.now().isoformat()
            })
            
            logger.info(f"Kafka failure test completed. Recovery ratio: {recovery_ratio:.2f}")
            
        except Exception as e:
            self.test_results[test_name].update({
                'status': 'failed',
                'error': str(e),
                'passed': False
            })
            logger.error(f"Kafka failure test failed: {e}")
    
    async def analyze_fault_tolerance_results(self):
        """Phân tích kết quả test fault tolerance"""
        
        print("\n" + "="*60)
        print("⚡ FAULT TOLERANCE TEST RESULTS")
        print("="*60)
        
        total_tests = len(self.test_results)
        passed_tests = sum(1 for result in self.test_results.values() if result.get('passed', False))
        
        print(f"📊 Total Tests: {total_tests}")
        print(f"✅ Passed: {passed_tests}")
        print(f"❌ Failed: {total_tests - passed_tests}")
        print(f"📈 Success Rate: {(passed_tests/total_tests*100):.1f}%")
        
        print("\n" + "-"*60)
        print("📋 DETAILED RESULTS:")
        print("-"*60)
        
        for test_name, result in self.test_results.items():
            status_icon = "✅" if result.get('passed', False) else "❌"
            print(f"{status_icon} {test_name.replace('_', ' ').title()}")
            print(f"   Status: {result.get('status', 'unknown')}")
            
            if 'error' in result:
                print(f"   Error: {result['error']}")
            
            if 'throughput_degradation' in result:
                print(f"   Performance Impact: {result['throughput_degradation']}")
            
            if 'recovery_ratio' in result:
                print(f"   Recovery: {result['recovery_ratio']}")
            
            print()
        
        # Overall assessment
        overall_pass = passed_tests >= total_tests * 0.8  # 80% pass rate
        print("="*60)
        print(f"🏆 OVERALL FAULT TOLERANCE: {'PASS' if overall_pass else 'FAIL'}")
        print("="*60)

async def main():
    """Main test runner"""
    print("⚡ Starting Fault Tolerance Testing Suite")
    
    tester = FaultToleranceTester()
    
    # Establish baseline
    await tester.establish_baseline()
    
    # Run fault tolerance tests
    print("\n🔥 Running fault tolerance tests...")
    
    await tester.test_kafka_node_failure()
    
    # Analyze results
    await tester.analyze_fault_tolerance_results()
    
    print("\n✅ Fault Tolerance Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 
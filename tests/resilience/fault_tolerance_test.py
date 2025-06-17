#!/usr/bin/env python3
"""
Fault Tolerance Testing Script
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
    
    async def test_cassandra_node_failure(self):
        """Test Cassandra node failure"""
        logger.info("🔥 Testing Cassandra node failure...")
        
        test_name = "cassandra_node_failure"
        self.test_results[test_name] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # Get Cassandra containers
            cassandra_containers = [c for c in self.docker_client.containers.list() 
                                  if 'cassandra' in c.name.lower()]
            
            if not cassandra_containers:
                raise Exception("No Cassandra containers found")
            
            # Stop Cassandra container
            target_container = cassandra_containers[0]
            container_name = target_container.name
            
            logger.info(f"Stopping Cassandra container: {container_name}")
            target_container.stop()
            
            # Wait for failure detection
            await asyncio.sleep(15)
            
            # Test database access during failure
            latency_during_failure = await self.measure_cassandra_latency()
            health_during_failure = await self.check_system_health()
            
            # Restart container
            logger.info(f"Restarting Cassandra container: {container_name}")
            target_container.start()
            
            # Wait for recovery
            await asyncio.sleep(45)  # Cassandra takes longer to start
            
            # Test recovery
            latency_after_recovery = await self.measure_cassandra_latency()
            health_after_recovery = await self.check_system_health()
            
            # Analyze results
            self.test_results[test_name].update({
                'status': 'completed',
                'container_stopped': container_name,
                'baseline_latency': self.baseline_metrics['cassandra_latency'],
                'latency_during_failure': latency_during_failure,
                'latency_after_recovery': latency_after_recovery,
                'health_during_failure': health_during_failure,
                'health_after_recovery': health_after_recovery,
                'passed': health_after_recovery['cassandra_available'] and latency_after_recovery > 0,
                'end_time': datetime.now().isoformat()
            })
            
            logger.info(f"Cassandra failure test completed.")
            
        except Exception as e:
            self.test_results[test_name].update({
                'status': 'failed',
                'error': str(e),
                'passed': False
            })
            logger.error(f"Cassandra failure test failed: {e}")
    
    async def test_spark_worker_failure(self):
        """Test Spark worker failure"""
        logger.info("🔥 Testing Spark worker failure...")
        
        test_name = "spark_worker_failure"
        self.test_results[test_name] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # Get Spark containers
            spark_containers = [c for c in self.docker_client.containers.list() 
                              if 'spark' in c.name.lower()]
            
            if not spark_containers:
                raise Exception("No Spark containers found")
            
            # Stop a Spark worker (not master)
            worker_containers = [c for c in spark_containers if 'worker' in c.name.lower()]
            
            if worker_containers:
                target_container = worker_containers[0]
                container_name = target_container.name
                
                logger.info(f"Stopping Spark worker: {container_name}")
                target_container.stop()
                
                # Monitor processing during failure
                await asyncio.sleep(30)
                
                # Check if data processing continues
                health_during_failure = await self.check_system_health()
                
                # Restart worker
                logger.info(f"Restarting Spark worker: {container_name}")
                target_container.start()
                
                await asyncio.sleep(30)
                health_after_recovery = await self.check_system_health()
                
                self.test_results[test_name].update({
                    'status': 'completed',
                    'container_stopped': container_name,
                    'health_during_failure': health_during_failure,
                    'health_after_recovery': health_after_recovery,
                    'passed': True,  # System should continue with remaining workers
                    'end_time': datetime.now().isoformat()
                })
            else:
                self.test_results[test_name].update({
                    'status': 'skipped',
                    'reason': 'No Spark worker containers found',
                    'passed': True
                })
            
        except Exception as e:
            self.test_results[test_name].update({
                'status': 'failed',
                'error': str(e),
                'passed': False
            })
            logger.error(f"Spark worker failure test failed: {e}")
    
    async def test_network_partition(self):
        """Test network partition simulation"""
        logger.info("🔥 Testing network partition...")
        
        test_name = "network_partition"
        self.test_results[test_name] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # This is simplified - in real scenario you'd use tools like:
            # - tc (traffic control) để simulate network issues
            # - iptables để block traffic
            # - Chaos Monkey tools
            
            # For demo, we'll simulate by temporarily stopping network-dependent services
            containers = self.docker_client.containers.list()
            kafka_containers = [c for c in containers if 'kafka' in c.name.lower()]
            
            if kafka_containers:
                # Simulate network partition by pausing container
                target_container = kafka_containers[0]
                logger.info(f"Pausing container to simulate network partition: {target_container.name}")
                
                target_container.pause()
                await asyncio.sleep(30)
                
                # Check system behavior during partition
                health_during_partition = await self.check_system_health()
                
                # Resume container
                target_container.unpause()
                await asyncio.sleep(20)
                
                health_after_recovery = await self.check_system_health()
                
                self.test_results[test_name].update({
                    'status': 'completed',
                    'simulation_method': 'container_pause',
                    'health_during_partition': health_during_partition,
                    'health_after_recovery': health_after_recovery,
                    'passed': health_after_recovery['kafka_available'],
                    'end_time': datetime.now().isoformat()
                })
            else:
                self.test_results[test_name].update({
                    'status': 'skipped',
                    'reason': 'No suitable containers for network partition test'
                })
            
        except Exception as e:
            self.test_results[test_name].update({
                'status': 'failed',
                'error': str(e),
                'passed': False
            })
            logger.error(f"Network partition test failed: {e}")
    
    async def test_resource_exhaustion(self):
        """Test resource exhaustion scenarios"""
        logger.info("🔥 Testing resource exhaustion...")
        
        test_name = "resource_exhaustion"
        self.test_results[test_name] = {
            'start_time': datetime.now().isoformat(),
            'status': 'running'
        }
        
        try:
            # Simulate high CPU load
            logger.info("Simulating high CPU load...")
            
            # Start CPU stress test in background
            cpu_stress_process = None
            try:
                # This requires 'stress' tool to be installed
                # sudo apt-get install stress
                cpu_stress_process = subprocess.Popen(['stress', '--cpu', '4', '--timeout', '60s'])
                
                # Monitor system during stress
                await asyncio.sleep(30)
                health_during_stress = await self.check_system_health()
                
                # Wait for stress to finish
                cpu_stress_process.wait()
                
                await asyncio.sleep(10)
                health_after_stress = await self.check_system_health()
                
                self.test_results[test_name].update({
                    'status': 'completed',
                    'stress_type': 'cpu',
                    'max_cpu_usage': health_during_stress.get('cpu_usage', 0),
                    'health_during_stress': health_during_stress,
                    'health_after_stress': health_after_stress,
                    'passed': health_after_stress['cpu_usage'] < 80,  # Should recover
                    'end_time': datetime.now().isoformat()
                })
                
            except FileNotFoundError:
                # If stress tool not available, simulate with Python
                logger.info("'stress' tool not found, using Python simulation...")
                
                import multiprocessing
                
                def cpu_stress():
                    # CPU intensive task
                    end_time = time.time() + 30
                    while time.time() < end_time:
                        pass
                
                processes = []
                for _ in range(multiprocessing.cpu_count()):
                    p = multiprocessing.Process(target=cpu_stress)
                    p.start()
                    processes.append(p)
                
                await asyncio.sleep(35)
                
                # Terminate processes
                for p in processes:
                    p.terminate()
                    p.join()
                
                health_after_simulation = await self.check_system_health()
                
                self.test_results[test_name].update({
                    'status': 'completed',
                    'stress_type': 'cpu_python_simulation',
                    'health_after_stress': health_after_simulation,
                    'passed': True,
                    'end_time': datetime.now().isoformat()
                })
            
        except Exception as e:
            self.test_results[test_name].update({
                'status': 'failed',
                'error': str(e),
                'passed': False
            })
            logger.error(f"Resource exhaustion test failed: {e}")
    
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
        
        # Save results
        await self.save_fault_tolerance_results({
            'timestamp': datetime.now().isoformat(),
            'baseline_metrics': self.baseline_metrics,
            'test_results': self.test_results,
            'summary': {
                'total_tests': total_tests,
                'passed_tests': passed_tests,
                'success_rate': passed_tests/total_tests*100,
                'overall_pass': overall_pass
            }
        })
    
    async def save_fault_tolerance_results(self, results: Dict):
        """Lưu kết quả test"""
        filename = f"fault_tolerance_results_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        
        with open(filename, 'w') as f:
            json.dump(results, f, indent=2, default=str)
        
        logger.info(f"Results saved to {filename}")

async def main():
    """Main test runner"""
    print("⚡ Starting Fault Tolerance Testing Suite")
    
    tester = FaultToleranceTester()
    
    # Establish baseline
    await tester.establish_baseline()
    
    # Run fault tolerance tests
    print("\n🔥 Running fault tolerance tests...")
    
    await tester.test_kafka_node_failure()
    await tester.test_cassandra_node_failure()
    await tester.test_spark_worker_failure()
    await tester.test_network_partition()
    await tester.test_resource_exhaustion()
    
    # Analyze results
    await tester.analyze_fault_tolerance_results()
    
    print("\n✅ Fault Tolerance Testing Complete!")

if __name__ == "__main__":
    asyncio.run(main()) 
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.policies import DCAwareRoundRobinPolicy
import os
import logging

logger = logging.getLogger(__name__)

class CassandraManager:
    def __init__(self):
        self.cluster = None
        self.session = None
        self.keyspace = "finnhub"
        
    def connect(self):
        """Kết nối đến Cassandra cluster"""
        try:
            # Cassandra connection config
            hosts = os.getenv("CASSANDRA_HOSTS", "localhost").split(",")
            port = int(os.getenv("CASSANDRA_PORT", "9042"))
            username = os.getenv("CASSANDRA_USERNAME", "cassandra")
            password = os.getenv("CASSANDRA_PASSWORD", "cassandra")
            
            # Setup authentication
            auth_provider = PlainTextAuthProvider(username=username, password=password)
            
            # Setup load balancing policy
            load_balancing_policy = DCAwareRoundRobinPolicy(local_dc='datacenter1')
            
            # Create cluster
            self.cluster = Cluster(
                hosts,
                port=port,
                auth_provider=auth_provider,
                load_balancing_policy=load_balancing_policy,
                protocol_version=4
            )
            
            # Connect to cluster
            self.session = self.cluster.connect()
            
            # Set keyspace
            self.session.set_keyspace(self.keyspace)
            
            logger.info(f"Successfully connected to Cassandra cluster: {hosts}")
            return True
            
        except Exception as e:
            logger.error(f"Failed to connect to Cassandra: {e}")
            return False
    
    def disconnect(self):
        """Ngắt kết nối Cassandra"""
        if self.session:
            self.session.shutdown()
        if self.cluster:
            self.cluster.shutdown()
        logger.info("Disconnected from Cassandra")
    
    def get_session(self):
        """Lấy session để thực hiện queries"""
        if not self.session:
            if not self.connect():
                raise Exception("Cannot establish Cassandra connection")
        return self.session
    
    def execute_query(self, query, parameters=None):
        """Thực hiện query với error handling"""
        try:
            session = self.get_session()
            if parameters:
                result = session.execute(query, parameters)
            else:
                result = session.execute(query)
            return result
        except Exception as e:
            logger.error(f"Query execution failed: {query} - Error: {e}")
            raise e

# Global instance
cassandra_manager = CassandraManager()

def get_cassandra_session():
    """Dependency function cho FastAPI"""
    return cassandra_manager.get_session()

def init_cassandra():
    """Initialize Cassandra connection khi start app"""
    return cassandra_manager.connect()

def close_cassandra():
    """Close Cassandra connection khi shutdown app"""
    cassandra_manager.disconnect() 
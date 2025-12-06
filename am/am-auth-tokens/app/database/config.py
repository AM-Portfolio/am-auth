"""Database configuration and session management"""
from typing import AsyncGenerator
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine, create_async_engine, async_sessionmaker
import os
from dotenv import load_dotenv
from .base import Base
from .models import AuthorizationCodeORM, TokenRecordORM

load_dotenv()


class DatabaseConfig:
    """Database configuration for Auth Tokens service"""
    
    def __init__(self):
        database_url = os.getenv('DATABASE_URL')
        
        if not database_url:
            db_host = os.getenv('DB_HOST', 'helium')
            db_port = os.getenv('DB_PORT', '5432')
            db_name = os.getenv('DB_NAME', 'heliumdb')
            db_user = os.getenv('DB_USER', 'postgres')
            db_password = os.getenv('DB_PASSWORD', 'postgres')
            
            if db_password:
                database_url = f'postgresql://{db_user}:{db_password}@{db_host}:{db_port}/{db_name}'
            else:
                database_url = f'postgresql://{db_user}@{db_host}:{db_port}/{db_name}'
        
        if database_url.startswith('postgresql://'):
            self.database_url = database_url.replace('postgresql://', 'postgresql+asyncpg://')
        else:
            self.database_url = database_url
        
        if '?sslmode=' in self.database_url:
            self.database_url = self.database_url.split('?sslmode=')[0]
        
        print("🔗 Auth Tokens connecting to database")
        
        self.engine: AsyncEngine = create_async_engine(
            self.database_url,
            echo=os.getenv('DB_ECHO', 'false').lower() == 'true',
            pool_size=int(os.getenv('DB_POOL_SIZE', '5')),
            max_overflow=int(os.getenv('DB_MAX_OVERFLOW', '10')),
            pool_timeout=int(os.getenv('DB_POOL_TIMEOUT', '30'))
        )
        
        self.async_session_factory = async_sessionmaker(
            bind=self.engine,
            class_=AsyncSession,
            expire_on_commit=False
        )
    
    async def create_tables(self):
        """Create database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def drop_tables(self):
        """Drop database tables"""
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.drop_all)
    
    async def get_session(self) -> AsyncGenerator[AsyncSession, None]:
        """Get async database session"""
        async with self.async_session_factory() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()
    
    async def close(self):
        """Close database engine"""
        await self.engine.dispose()


db_config = DatabaseConfig()

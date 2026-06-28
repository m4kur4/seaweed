from sqlalchemy import Column, BigInteger, Date, Integer, String, Text, TIMESTAMP, text
from database import Base

class Transaction(Base):
    __tablename__ = "transactions"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    transaction_date = Column(Date, nullable=False, index=True)
    transaction_amount = Column(Integer, nullable=False)
    transaction_type = Column(String(10), nullable=False) # 'income' or 'expence'
    description = Column(Text, nullable=True)
    created_at = Column(TIMESTAMP, nullable=False, server_default=text("CURRENT_TIMESTAMP"))
    updated_at = Column(
        TIMESTAMP,
        nullable=False,
        server_default=text("CURRENT_TIMESTAMP ON UPDATE CURRENT_TIMESTAMP")
    )
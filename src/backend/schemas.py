from pydantic import BaseModel, ConfigDict, Field
from datetime import date, datetime
from typing import Optional

# 取得時のレスポンス
class TransactionRead(BaseModel):
    model_config = ConfigDict(from_attributes=True) # ORMオブジェクトから変換を許可

    id: int
    transaction_date: date
    transaction_amount: int
    transaction_type: str
    description: str | None
    created_at: datetime
    updated_at: datetime

# 登録時のレスポンス
class TransactionCreate(BaseModel):
    model_config = ConfigDict(from_attributes=True) # ORMオブジェクトから変換を許可

    transaction_date: date = Field(..., description="変動日")
    transaction_amount: int = Field(..., ge=0, description="変動額(0以上)")
    transaction_type: str = Field(..., description="変動種別('income' or 'expense')")
    description: Optional[str] = Field(None, description="備考")

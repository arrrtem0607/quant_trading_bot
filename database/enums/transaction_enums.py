from enum import Enum

class TransactionType(str, Enum):
    PAYMENT = "payment"
    REFERRAL = "referral"
    WITHDRAWAL = "withdrawal"

class TransactionStatus(str, Enum):
    PENDING = "pending"
    CONFIRMED = "confirmed"
    FAILED = "failed"

from sqlalchemy.orm import Session
import models
import schemas
from logging_config import setup_logger

logger = setup_logger("order_service")

def create_order(db: Session, order: schemas.OrderCreate, user_id: int):
    db_order = models.Order(
        user_id=user_id,
        product=order.product,
        quantity=order.quantity,
        status="pending"
    )
    try:
        db.add(db_order)
        db.commit()
        db.refresh(db_order)
        logger.info("Order created", extra={"user_id": user_id, "order_id": db_order.id})
        return db_order
    except Exception as e:
        logger.error("Order creation failed", extra={"user_id": user_id, "error": str(e)})
        raise

def get_order(db: Session, order_id: int):
    order = db.query(models.Order).filter(models.Order.id == order_id).first()
    if order:
        logger.info("Order fetched", extra={"order_id": order_id, "user_id": order.user_id})
    return order

def get_orders_by_user(db: Session, user_id: int):
    orders = db.query(models.Order).filter(models.Order.user_id == user_id).all()
    logger.info("Fetched user orders", extra={"user_id": user_id, "count": len(orders)})
    return orders

def update_order(db: Session, order_id: int, user_id: int, update_data: schemas.OrderCreate):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user_id
    ).first()
    if not order:
        logger.warning("Order update failed: not found or not owned", extra={"order_id": order_id, "user_id": user_id})
        return None
    order.product = update_data.product
    order.quantity = update_data.quantity
    db.commit()
    db.refresh(order)
    logger.info("Order updated", extra={"order_id": order_id, "user_id": user_id})
    return order

def delete_order(db: Session, order_id: int, user_id: int):
    order = db.query(models.Order).filter(
        models.Order.id == order_id,
        models.Order.user_id == user_id
    ).first()
    if not order:
        logger.warning("Order deletion failed: not found or not owned", extra={"order_id": order_id, "user_id": user_id})
        return None
    db.delete(order)
    db.commit()
    logger.info("Order deleted", extra={"order_id": order_id, "user_id": user_id})
    return order
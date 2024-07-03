from sqlalchemy import Column,String
from entidades.base import Base
from flask import url_for

# Definição da tabela users
class User(Base):
    __tablename__ = 'users'
    
    UserName = Column(String(50), primary_key=True, nullable=False)
    Password = Column(String(80), nullable=False)
    Class = Column(String(50), nullable=False)

    def get_class_image(self):
        class_image_map = {
            "Peasant": "peasant.jpg",
            "Warrior": "warrior.jpg",
            "Wizard": "wizard.jpg",
            "Rogue": "rogue.jpg",
            "Cleric": "cleric.jpg",
            "Barbarian": "barbarian.jpg",
            "Druid": "druid.jpg",
            "Bard": "bard.jpg",
            "Paladin": "paladin.jpg"
        }
        return url_for('static', filename=class_image_map.get(self.Class, "peasant.jpg"))
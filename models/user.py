from . import db, bcrypt

class User(db.Model):
    """User"""

    __tablename__ = "users"

    username = db.Column(db.String(20), primary_key=True)
    password = db.Column(db.Text, nullable=False)
    email = db.Column(db.String(50), nullable=False, unique=True)
    first_name = db.Column(db.String(30), nullable=False)
    last_name = db.Column(db.String(30), nullable=False)
    profile_image = db.Column(db.String(200), nullable=True, default='https://th.bing.com/th?id=OIP.Ze_F6AGBDQyYrlbNF7tCXAHaHa&w=250&h=250&c=8&rs=1&qlt=90&o=6&pid=3.1&rm=2') 
    bio = db.Column(db.Text, nullable=True)
    recipes = db.relationship("Recipe", backref="user")

    @classmethod
    def signup(cls, username, pwd, email, fname, lname, bio, image):
        """Register user w/hashed password & return user."""
        hashed = bcrypt.generate_password_hash(pwd).decode("utf8")
        return cls(username=username, password=hashed, email=email, first_name=fname, last_name=lname, bio=bio, profile_image=image)

    @classmethod
    def authenticate(cls, username, pwd):
        """Validate that user exists & password is correct. Return user if valid; else return False."""
        u = User.query.filter_by(username=username).first()
        if u and bcrypt.check_password_hash(u.password, pwd):
            return u
        else:
            return False

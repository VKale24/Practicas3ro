class Company():

    def __init__(self, id=None, name= None, password=None, crypt=None, register_date= None, ip= None):
        self.id = id
        self.ip = ip
        self.name = name
        self.password = password
        self.crypt = crypt
        self.register_date = register_date

    def to_JSON(self):
        return {
        'id': self.id,
        'ip': self.ip,
        'name': self.name,
        'register_date': self.register_date
        }
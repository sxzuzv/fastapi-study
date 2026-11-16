from datetime import datetime, timedelta, timezone

import jwt

SECRET_KEY = 'haem-is-aehaem'

exp = datetime.now(timezone.utc) + timedelta(minutes=30)
token = jwt.encode({'sub': '1', 'exp': exp}, SECRET_KEY, algorithm='HS256')
print(token)

decoded_data = jwt.decode(token, SECRET_KEY, algorithms=['HS256'])
print(decoded_data)
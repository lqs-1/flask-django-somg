from ihome import create_app
from flask_script import Manager
from flask_migrate import Migrate, MigrateCommand
from ihome import db

app = create_app('product')
manager = Manager(app)
Migrate(app, db)
# 添加数据库生成迁移文件的命令
manager.add_command('db', MigrateCommand)

if __name__ == '__main__':
    manager.run()









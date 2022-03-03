from fdfs_client.client import Fdfs_client
from config import fdfs_config


def save(content):
    client = Fdfs_client(fdfs_config.CONFIG_FILE)
    rst = client.upload_by_buffer(content)

    if rst['Status'] != 'Upload successed.':
        raise Exception('文件存储失败')
    return rst['Remote file_id']
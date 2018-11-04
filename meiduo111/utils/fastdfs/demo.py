from fdfs_client.client import Fdfs_client

if __name__ == '__main__':
    client = Fdfs_client('client.conf')
    ret = client.upload_by_file('/home/python/Desktop/11.jpg')
    print(ret)
    '''
    {'Group name': 'group1',
     'Remote file_id': 'group1/M00/00/00/wKj3nFvdI-CAIS_OAAAbNfbF1N8913.jpg',
      'Status': 'Upload successed.',
       'Local file name': '/home/python/Desktop/11.jpg', 
       'Uploaded size': '6.00KB', 
       'Storage IP': '192.168.247.156'}

    '''
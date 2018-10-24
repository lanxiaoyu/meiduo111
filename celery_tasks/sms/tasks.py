
from celery_tasks.main import app
from meiduo111.utils.ytx_sdk.sendSMS import CCP


@app.task(name='send_sms_code')
def send_sms_code(mobile, code, expires, template_id):
    CCP.sendTemplateSMS(mobile,code,expires,template_id)
    print(code)

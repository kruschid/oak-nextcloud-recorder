import requests
from recorder import recorder
from config import config
from webdav3.client import Client
from reactivex import Observer, operators as op, create, timer
import os

options = {
    'webdav_hostname': config['WEBDAV_HOSTNAME'],
    'webdav_login':    config['WEBDAV_LOGIN'],
    'webdav_password': config['WEBDAV_PASSWORD'],
}

client = Client(options)


def upload_recording(path):
    def create_uploader(observer: Observer, scheduler):
        print('uploading file {}'.format(path))

        def on_completed():
            print('uploaded completed: {}'.format(path))
            observer.on_next(path)
            observer.on_completed()

        kwargs = {
            'remote_path': 'recordings/{}'.format(path),
            'local_path':  path,
            'callback': on_completed
        }
        try:
            client.upload_async(**kwargs)
        except:
            observer.on_error('something wrong')

    def error_handler(e, source):
        print('upload failed for {}'.format(path))
        print('error: {}'.format(e))
        print('retrying in 5 seconds...')
        return timer(5).pipe(
            op.flat_map(lambda _: source)
        )

    return create(create_uploader).pipe(
        op.catch(error_handler)
    )


def remove_temprary_file(path: str):
    if os.path.isfile(path):
        os.remove(path)


def notify(path: str):
    requests.get(
        'https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage?chat_id={TELEGRAM_CHAT_ID}&text=oak-nextcloud-recorder%20new%20recording:%20{PATH}'.format(
            TELEGRAM_TOKEN=config['TELEGRAM_TOKEN'],
            TELEGRAM_CHAT_ID=config['TELEGRAM_CHAT_ID'],
            PATH=path,
        ),
        timeout=3
    )


uploader = recorder.pipe(
    op.flat_map(upload_recording),
    op.do_action(on_next=remove_temprary_file),
    op.do_action(on_next=notify),
)

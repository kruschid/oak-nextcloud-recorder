from camera import camera
import cv2
from reactivex import operators as op
import time
from labels import LABEL_MAP
from datetime import datetime

is_recording = False


def has_detected_person(payload: tuple[cv2.Mat, list]):
    return any(
        map(
            lambda d: LABEL_MAP[d.label] == "person", payload[1]
        )
    )


def record(payload: tuple[cv2.Mat, list]):
    global is_recording
    is_recording = True

    file_path = '{}.avi'.format(datetime.now())
    print('start recording: {} ...'.format(file_path))

    latest_detection_timestamp = time.time()

    fourcc = cv2.VideoWriter_fourcc(*'XVID')
    out = cv2.VideoWriter(
        file_path,
        fourcc,
        10.0,
        (300, 300),
    )

    def should_continue_recording(payload):
        nonlocal latest_detection_timestamp
        if has_detected_person(payload):
            latest_detection_timestamp = time.time()

        print(latest_detection_timestamp)

        return time.time() - latest_detection_timestamp < 5

    def on_next_frame(payload):
        out.write(payload[0])

    def finish_recording():
        print('...finish recording')
        global is_recording
        is_recording = False
        out.release()

    return camera.pipe(
        op.take_while(should_continue_recording),
        op.do_action(
            on_next=on_next_frame,
            on_completed=finish_recording,
        ),
        op.last(),
        op.map(lambda payload: file_path),
    )


def should_start_recording(payload: tuple[cv2.Mat, list]):
    return not is_recording and has_detected_person(payload)


recorder = camera.pipe(
    op.filter(should_start_recording),
    op.flat_map(record),
    op.do_action(on_next=lambda path: print(path))
)

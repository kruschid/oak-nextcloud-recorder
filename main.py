import asyncio
import cv2  # opencv - display the video stream
import numpy as np
from reactivex import merge, operators as op
from reactivex.scheduler.eventloop import AsyncIOScheduler
import signal
import sys
from camera import camera
from recorder import recorder
from uploader import uploader

labelMap = ["background", "aeroplane", "bicycle", "bird", "boat", "bottle", "bus", "car", "cat", "chair", "cow",
            "diningtable", "dog", "horse", "motorbike", "person", "pottedplant", "sheep", "sofa", "train", "tvmonitor"]


def frameNorm(frame, bbox):
    normVals = np.full(len(bbox), frame.shape[0])
    normVals[::2] = frame.shape[1]
    return (np.clip(np.array(bbox), 0, 1) * normVals).astype(int)


def putText(frame: cv2.Mat, text: str, coords: tuple[int, int]):
    cv2.putText(
        img=frame,
        text=text,
        org=coords,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=(0, 0, 0),
        thickness=3,
        lineType=cv2.LINE_AA
    )
    cv2.putText(
        img=frame,
        text=text,
        org=coords,
        fontFace=cv2.FONT_HERSHEY_SIMPLEX,
        fontScale=0.5,
        color=(255, 255, 255),
        thickness=1,
        lineType=cv2.LINE_AA
    )


def show_video(payload: tuple[cv2.Mat, any]):
    [frame, detections] = payload
    for detection in detections:
        bbox = frameNorm(frame, (detection.xmin, detection.ymin,
                         detection.xmax, detection.ymax))
        cv2.rectangle(frame, (bbox[0], bbox[1]),
                      (bbox[2], bbox[3]), (255, 0, 0), 2)
        putText(frame, labelMap[detection.label], (bbox[0] + 10, bbox[1] + 20))
        putText(frame, f"{int(detection.confidence * 100)}%",
                (bbox[0] + 10, bbox[1] + 40))

    cv2.imshow("preview", frame)
    cv2.waitKey(1)  # without this preview window doesn't show up


loop = asyncio.new_event_loop()
aio_scheduler = AsyncIOScheduler(loop=loop)

subscription = merge(
    # camera.pipe(op.do_action(on_next=show_video,)),
    recorder,
    uploader,
).subscribe(
    on_completed=lambda: print('finito'),
    scheduler=aio_scheduler,
)


def signal_handler(sig, frame):
    print('You pressed Ctrl+C!')
    subscription.dispose()
    loop.stop()
    sys.exit(0)


signal.signal(signal.SIGINT, signal_handler)

loop.run_forever()

import depthai  # depthai - access the camera and its data packets
from reactivex import timer, operators as op
import blobconverter

pipeline = depthai.Pipeline()

cam_rgb = pipeline.create(depthai.node.ColorCamera)
cam_rgb.setPreviewSize(300, 300)
cam_rgb.setInterleaved(False)

detection_nn = pipeline.create(depthai.node.MobileNetDetectionNetwork)
# Set path of the blob (NN model). We will use blobconverter to convert&download the model
# detection_nn.setBlobPath("/path/to/model.blob")
detection_nn.setBlobPath(blobconverter.from_zoo(
    name='mobilenet-ssd', shaves=6))
detection_nn.setConfidenceThreshold(0.5)
cam_rgb.preview.link(detection_nn.input)

xout_rgb = pipeline.create(depthai.node.XLinkOut)
xout_rgb.setStreamName("rgb")
cam_rgb.preview.link(xout_rgb.input)

xout_nn = pipeline.create(depthai.node.XLinkOut)
xout_nn.setStreamName("nn")
detection_nn.out.link(xout_nn.input)

device = depthai.Device(pipeline, usb2Mode=True)


q_rgb = device.getOutputQueue("rgb", maxSize=1, blocking=False)
q_nn = device.getOutputQueue("nn", maxSize=1, blocking=False)


def get_frame(i):
    frame = None
    detections = []

    in_rgb = q_rgb.tryGet()
    in_nn = q_nn.tryGet()

    if in_rgb is not None:
        frame = in_rgb.getCvFrame()

    if in_nn is not None:
        detections = in_nn.detections

    return [frame, detections]


camera = timer(1, 0.1).pipe(
    op.map(get_frame),
    op.filter(lambda payload: payload[0] is not None),
    op.share(),
)

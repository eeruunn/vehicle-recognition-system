import cv2
import torch
import serial.tools.list_ports

ports = serial.tools.list_ports.comports()
serialInst = serial.Serial()
portsList = []

for one in ports:
    portsList.append(str(one))
    print(str(one))

serialInst.baudrate = 9600
serialInst.port = "COM3"
serialInst.open()
previouscom = "0"
serialInst.write(previouscom.encode('utf-8'))
model = torch.hub.load('ultralytics/yolov5', 'yolov5s')

cap = cv2.VideoCapture(2)

screen_width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
section_width = screen_width // 3

leds = [1, 1, 1]


def write_data(led1, led2, led3):
    delim = bytes(';', "utf-8")
    serialInst.write(bytes(str(led1), "utf-8"))
    serialInst.write(delim)
    serialInst.write(bytes(str(led2), "utf-8"))
    serialInst.write(delim)
    serialInst.write(bytes(str(led3), "utf-8"))
    serialInst.write(delim)

    return 1


while True:
    ret, frame = cap.read()
    if not ret:
        break

    results = model(frame)

    detected_sections = set()
    name = ""
    for box in results.xyxy[0].numpy():
        x1, y1, x2, y2, confidence, cls = box
        centroid_x = (x1 + x2) / 2

        if centroid_x < section_width:
            detected_sections.add(1)
        elif centroid_x < 2 * section_width:
            detected_sections.add(2)
        else:
            detected_sections.add(3)

        label = results.names[int(cls)]
        name = label
        color = (255, 0, 0)
        cv2.rectangle(frame, (int(x1), int(y1)), (int(x2), int(y2)), color, 2)
        cv2.putText(frame, label, (int(x1), int(y1) - 10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, color, 2)

    if len(detected_sections) != 0:
        vehicles = ["car", "bus", "truck"]
        if name in vehicles:
            command = detected_sections
            if 1 in detected_sections:
                leds[0] = 0
            else:
                leds[0] = 1

            if 2 in detected_sections:
                leds[1] = 0
            else:
                leds[1] = 1

            if 3 in detected_sections:
                leds[2] = 0
            else:
                leds[2] = 1
            print(command)
            previouscom = command
            write_data(leds[0], leds[1], leds[2])

    else:
        command = "0"
        write_data(1, 1, 1)
        print(command)

    cv2.imshow("Frame", frame)

    if cv2.waitKey(1) & 0xFF == ord('q'):
        break

cap.release()
cv2.destroyAllWindows()

import cv2
import os

def capture_face(name):
    dataset_path = "dataset"

    if not os.path.exists(dataset_path):
        os.makedirs(dataset_path)

    cap = cv2.VideoCapture(0)

    print("Press SPACE to capture image")

    while True:
        ret, frame = cap.read()
        cv2.imshow("Capture Face", frame)

        if cv2.waitKey(1) == 32:  # SPACE key
            file_path = os.path.join(dataset_path, f"{name}.jpg")
            cv2.imwrite(file_path, frame)
            break

    cap.release()
    cv2.destroyAllWindows()

    return file_path
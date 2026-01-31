import mmap
import ctypes
import cv2
import os

# ---------- MUST MATCH C ----------
SHM_NAME = "/ipc_dog_shm"
MAX_BOXES = 10

class Detection(ctypes.Structure):
    _fields_ = [
        ("class_id", ctypes.c_int),
        ("confidence", ctypes.c_float),
        ("x", ctypes.c_int),
        ("y", ctypes.c_int),
        ("w", ctypes.c_int),
        ("h", ctypes.c_int),
    ]

class SharedData(ctypes.Structure):
    _fields_ = [
        ("count", ctypes.c_int),
        ("det", Detection * MAX_BOXES),
    ]

def main():
    image_path = "dog.jpg"

    # Linux / WSL shared memory path
    fd = os.open("/dev/shm" + SHM_NAME, os.O_RDONLY)

    shm = mmap.mmap(
        fd,
        ctypes.sizeof(SharedData),
        mmap.MAP_SHARED,
        mmap.PROT_READ
    )

    shared = SharedData.from_buffer_copy(shm)

    print("Detections read from shared memory:", shared.count)

    img = cv2.imread(image_path)
    if img is None:
        print("Failed to load image")
        return

    for i in range(shared.count):
        d = shared.det[i]

        x, y, w, h = d.x, d.y, d.w, d.h
        conf = d.confidence

        cv2.rectangle(
            img,
            (x, y),
            (x + w, y + h),
            (0, 255, 0),
            2
        )

        label = f"dog {conf:.2f}"
        cv2.putText(
            img,
            label,
            (x, y - 10),
            cv2.FONT_HERSHEY_SIMPLEX,
            0.7,
            (0, 255, 0),
            2
        )

    cv2.imwrite("ipc_dog_out.jpg", img)
    print("Output saved as ipc_dog_out.jpg")

    shm.close()
    os.close(fd)

if __name__ == "__main__":
    main()

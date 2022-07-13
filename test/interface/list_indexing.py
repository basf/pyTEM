

class Camera:

    def __init__(self, name):
        self.name = name


if __name__ == "__main__":
    # desired_camera_name = 'BM-Ceta'
    desired_camera_name = 'Fred'

    supported_cameras = [Camera('BM-Ceta'), Camera('BM-Falcon')]
    desired_camera_obj = supported_cameras[[c.name for c in supported_cameras].index(desired_camera_name)]

    print(desired_camera_obj.name)

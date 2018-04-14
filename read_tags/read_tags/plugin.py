from pydicom import Dataset


class Plugin:
    def process(self, img: Dataset):
        return str(img.PatientName)

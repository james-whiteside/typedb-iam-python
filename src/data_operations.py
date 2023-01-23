import src.data_generation as data_generation


def generate_new_dataset():
    data = data_generation.generate_data()
    data_generation.save_data(data)

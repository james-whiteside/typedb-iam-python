import src.io_controller as io_controller
import src.data_builder as data_builder
import src.client as client


io_controller.create_log()
data = data_builder.generate_data()
data_builder.save_data(data)
io_controller.kill()

data = data_builder.load_data()
client.run_client()

from Include import model as mod
import config

model = mod.create_base_model()
model.save(f"{config.MODELS_DIR}1.keras")
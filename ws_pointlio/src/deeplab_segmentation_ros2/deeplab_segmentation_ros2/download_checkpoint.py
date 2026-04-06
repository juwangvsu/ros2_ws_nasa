
from pathlib import Path

import torch
from torchvision.models.segmentation import (
    DeepLabV3_ResNet50_Weights,
    deeplabv3_resnet50,
)


def main() -> None:
    out_path = Path("deeplabv3_resnet50_coco_voc.pth")
    weights = DeepLabV3_ResNet50_Weights.COCO_WITH_VOC_LABELS_V1
    model = deeplabv3_resnet50(weights=weights)
    torch.save(model.state_dict(), out_path)
    print(f"Saved checkpoint to {out_path.resolve()}")


if __name__ == "__main__":
    main()

from IPython.display import display, HTML
import cv2
import numpy as np
from google.colab.patches import cv2_imshow


def crop_image(image_path):
  # 이미지 읽기
  image = cv2.imread(image_path)

  # HTML 및 JavaScript 코드
  html_code = """
  <div>
    <canvas id="canvas"></canvas>
  </div>
  <script>
    const imageSrc = '{data}';
    const canvas = document.getElementById('canvas');
    const ctx = canvas.getContext('2d');
    const image = new Image();

    image.src = imageSrc;
    image.onload = () => {{
      canvas.width = image.width;
      canvas.height = image.height;
      ctx.drawImage(image, 0, 0);
    }};

    let startX, startY, endX, endY, isDragging = false;

    canvas.addEventListener('mousedown', (e) => {{
      startX = e.offsetX;
      startY = e.offsetY;
      isDragging = true;
    }});

    canvas.addEventListener('mousemove', (e) => {{
      if (isDragging) {{
        ctx.drawImage(image, 0, 0);
        ctx.strokeStyle = 'red';
        ctx.lineWidth = 2;
        ctx.strokeRect(startX, startY, e.offsetX - startX, e.offsetY - startY);
      }}
    }});

    canvas.addEventListener('mouseup', (e) => {{
      endX = e.offsetX;
      endY = e.offsetY;
      isDragging = false;
      
      const region = {{
        x: Math.min(startX, endX),
        y: Math.min(startY, endY),
        width: Math.abs(endX - startX),
        height: Math.abs(endY - startY)
      }};
      google.colab.kernel.invokeFunction('notebook.getCropRegion', [region], {{}});
    }});

    document.addEventListener('keydown', (e) => {{
      if (e.key === 'Enter') {{
        google.colab.kernel.invokeFunction('notebook.saveCroppedRegion', [], {{}});
      }}
    }});
  </script>
  """

  # Base64로 이미지 데이터를 인코딩
  import base64
  _, buffer = cv2.imencode('.jpg', image)
  image_data = base64.b64encode(buffer).decode()

  # HTML 표시
  display(HTML(html_code.format(data=f"data:image/jpeg;base64,{image_data}")))

  # JavaScript로부터 영역 좌표 받기
  from google.colab import output

  crop_region = None

  def get_crop_region(region):
      global crop_region
      crop_region = region
      print("Crop region received:", crop_region)

  output.register_callback('notebook.getCropRegion', get_crop_region)

  # 엔터 키를 눌렀을 때 저장 처리
  def save_cropped_region():
      global crop_region
      if crop_region:
          x, y, width, height = crop_region['x'], crop_region['y'], crop_region['width'], crop_region['height']
          cropped_image = image[y:y+height, x:x+width]

          # 결과 표시
          cv2_imshow(cropped_image)

          # 저장
          cv2.imwrite(image_path.replace('.png','_crop.png'), cropped_image)
          print(f"Cropped image saved as {image_path.replace('.png','_crop.png')}")
      else:
          print("No region selected. Please select a region before pressing Enter.")

  output.register_callback('notebook.saveCroppedRegion', save_cropped_region)

  # 안내 메시지
  print("Draw a rectangle on the image and press Enter to save the cropped region.")

if __name__=="__main__":
  crop_image('/content/SimpleHTR/data/DKU1.png')

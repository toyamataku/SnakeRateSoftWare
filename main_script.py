# -*- coding: utf-8 -*-
"""
main_script.py

4つの大きな関数 (select_multipliers, process_image_livewire,
process_circle_intersections, process_image_3code) は
すでに各 .pyx ファイルへ移して Cython 化している想定。

このスクリプトは「それ以外の処理 (GUI, Excel出力, ファイル削除, メインループ等)」
だけを残し、4つの関数はバイナリ (.pyd/.so) から import して呼び出す。
"""

import os
import pandas as pd
import cv2
import numpy as np

# GUI関連
from tkinter import Toplevel, Checkbutton, IntVar, Button, filedialog, Tk
from tkinter import messagebox

# ============================
# ここがポイント: 4つのCythonバイナリをimport
# ============================
import my_select_multipliers            # => select_multipliers()
import my_process_image_livewire        # => process_image_livewire()
import my_process_circle_intersections  # => process_circle_intersections()
import my_process_image_3code           # => process_image_3code()

########################################
# GUI / Utility Functions
########################################

def select_image_file():
    """
    Open a file dialog to select an image file.
    Supported image formats: jpg, jpeg, png, bmp.
    Returns the selected file path.
    """
    root = Tk()
    root.withdraw()
    file_path = filedialog.askopenfilename(
        filetypes=[("Image files", "*.jpg;*.jpeg;*.png;*.bmp")]
    )
    root.destroy()
    return file_path

def show_message(title, message):
    """
    Display a popup message box with a given title and message.
    """
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    root.lift()
    root.after(0, root.lift)
    messagebox.showinfo(title, message, master=root)
    root.destroy()

########################################
# Main Loop
########################################

if __name__ == "__main__":
    root = Tk()
    root.withdraw()
    try:
        while True:
            # ---- 1) 画像ファイル選択 ----
            image_path = select_image_file()
            if image_path == '':
                print("No file selected, exiting...")
                break

            image = cv2.imread(image_path)
            if image is None:
                print("Invalid image. Exiting...")
                break

            height, width, _ = image.shape
            print(f"Image size: {width}x{height} (Width x Height)")

            # ---- 2) GUIで円をクリックして、multiplier選択を呼び出す ----
            #     => バイナリ化された my_select_multipliers.select_multipliers() を使用
            circles_info = []
            points = []
            circle_completed = False

            def click_event_circle(event, x, y, flags, param):
                """
                マウスクリックで2点→ 円の中心・半径決定。
                さらに my_select_multipliers.select_multipliers() で倍率を選択。
                """
                global points, image, circles_info, circle_completed
                if event == cv2.EVENT_LBUTTONDOWN:
                    points.append((x, y))
                    cv2.circle(image, (x, y), 5, (255, 0, 0), -1)
                    cv2.imshow('image', image)
                    cv2.setWindowProperty('image', cv2.WND_PROP_TOPMOST, 1)

                    if len(points) == 1:
                        show_message("Information", "Click the other end of the disc edge")
                    elif len(points) == 2:
                        point1, point2 = points
                        radius = int(np.linalg.norm(np.array(point1) - np.array(point2)) / 2)
                        center = (
                            (point1[0] + point2[0]) // 2,
                            (point1[1] + point2[1]) // 2
                        )
                        # ==== Cythonバイナリから関数を呼ぶ ====
                        selected_multipliers = my_select_multipliers.select_multipliers()
                        for multiplier in selected_multipliers:
                            current_radius = radius * multiplier
                            cv2.circle(image, center, current_radius, (0, 255, 255), 1)
                            circles_info.append({
                                'FileName': os.path.basename(image_path),
                                'Multiplier': multiplier,
                                'CenterX': center[0],
                                'CenterY': center[1],
                                'Radius': current_radius
                            })
                        cv2.imshow('image', image)
                        points.clear()
                        circle_completed = True

            show_message("Information", "Click one end of the disc edge")
            cv2.imshow('image', image)
            cv2.setWindowProperty('image', cv2.WND_PROP_TOPMOST, 1)
            cv2.setMouseCallback('image', click_event_circle)

            # 円クリック用のループ
            while True:
                key = cv2.waitKey(1)
                if key & 0xFF == ord('q'):
                    break
                if circle_completed:
                    cv2.waitKey(1000)
                    break

            # ---- 円情報をExcel保存 → circles.png保存 ----
            excel_file_name = image_path.rsplit(".", 1)[0] + "_circles.xlsx"
            output_path = image_path.rsplit(".", 1)[0] + "_circles.png"
            cv2.imwrite(output_path, image)
            print(f"Image saved as {output_path}")

            import pandas as pd
            df = pd.DataFrame(circles_info)
            df.to_excel(excel_file_name, index=False)
            print(f"Circle data saved as {excel_file_name}")

            cv2.destroyAllWindows()

            # ---- 3) Livewireセグメント ----
            #   => バイナリから process_image_livewire() を呼ぶ
            lw_result = my_process_image_livewire.process_image_livewire(image_path)
            if lw_result is None:
                print("Skipping the main code processing (livewire result is None).")
                break
            folder, FirstThreeWords, output_path_canvas2, output_path_excel, extra_paths = lw_result

            # ---- 4) 3code処理 ----
            #   => バイナリから process_image_3code() を呼ぶ
            circle_results = my_process_image_3code.process_image_3code(
                output_path_canvas2, folder, FirstThreeWords, None
            )

            if circle_results:
                output_excel_filename = os.path.join(folder, "result.xlsx")
                df_results = pd.DataFrame(circle_results)

                # Bend列の整形
                bend_columns = [
                    col for col in df_results.columns
                    if 'Bend' in col and 'External_Angle' in col
                ]
                max_bends = 0
                if bend_columns:
                    # BendN_External_Angle のNを取り出して最大値を調べる
                    max_bends = max([
                        int(col.replace('Bend','').replace('_External_Angle',''))
                        for col in bend_columns
                    ] + [0])

                # 存在しないBend列があれば作る
                for i in range(1, max_bends+1):
                    if f'Bend{i}_External_Angle' not in df_results.columns:
                        df_results[f'Bend{i}_External_Angle'] = None

                ordered_columns = [
                    'File Name', 'Multiplier', 'Intersection Number', 'Number of Bends'
                ]
                for i in range(1, max_bends+1):
                    ordered_columns.append(f'Bend{i}_External_Angle')
                ordered_columns.append('Total Meandering Angle at All Bends')

                df_results = df_results[ordered_columns]
                df_results.to_excel(output_excel_filename, index=False)
                print(f"All images' results have been saved to Excel: {output_excel_filename}")

                # ---- 不要ファイル削除 (例) ----
                if output_path_canvas2 and os.path.exists(output_path_canvas2):
                    os.remove(output_path_canvas2)
                if output_path_excel and os.path.exists(output_path_excel):
                    os.remove(output_path_excel)
                if extra_paths:
                    for p in extra_paths:
                        if p and os.path.exists(p):
                            os.remove(p)
                if os.path.exists(excel_file_name):
                    os.remove(excel_file_name)
                if os.path.exists(output_path):
                    os.remove(output_path)
            else:
                print("No processed results are available.")

            print("Processing finished.")
            break
    finally:
        root.destroy()

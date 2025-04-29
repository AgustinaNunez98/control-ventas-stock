import tkinter as tk
from tkinter import ttk, messagebox
import pandas as pd
from datetime import datetime

# Cargar archivo Excel
archivo = "Gastos y ganancias.xlsx"
recetas_df = pd.read_excel(archivo, sheet_name="Recetas")
ingredientes_df = pd.read_excel(archivo, sheet_name="Ingredientes")
pedidos_df = pd.read_excel(archivo, sheet_name="Pedidos")

# Limpiar recetas
recetas_df = recetas_df.dropna(subset=["RECETA"])
recetas_disponibles = recetas_df['RECETA'].unique()

# Función para registrar la venta
def registrar_venta():
    producto = combo_producto.get()
    cantidad_str = entry_cantidad.get()
    precio_str = entry_precio.get()

    if not cantidad_str.isdigit() or not precio_str.replace(".", "").isdigit():
        messagebox.showerror("Error", "Ingresá cantidad y precio válidos.")
        return

    cantidad = int(cantidad_str)
    precio_venta = float(precio_str)

    receta = recetas_df[recetas_df['RECETA'] == producto]
    costo_unitario = receta['SUBTOTAL'].sum()
    costo_total = costo_unitario * cantidad
    ganancia = precio_venta - costo_total

    # Descontar del stock
    for _, row in receta.iterrows():
        ingrediente = row['INGREDIENTE']
        cantidad_usada = row['CANTIDAD USADA'] * cantidad
        mask = ingredientes_df['NOMBRE INGREDIENTE'] == ingrediente
        if mask.any():
            ingredientes_df.loc[mask, 'STOCK ACTUAL'] -= cantidad_usada

    # Registrar la venta
    nuevo = {
        "Cliente": "Venta directa",
        "Producto": producto,
        "Cantidad": cantidad,
        "Precio": precio_venta,
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Aclaración": f"Ganancia: ${ganancia:.2f} | Costo: ${costo_total:.2f}"
    }
    pedidos_df.loc[len(pedidos_df)] = nuevo

    # Guardar cambios
    with pd.ExcelWriter(archivo, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
        ingredientes_df.to_excel(writer, sheet_name="Ingredientes", index=False)
        pedidos_df.to_excel(writer, sheet_name="Pedidos", index=False)

    messagebox.showinfo("Venta registrada", f"Venta de {cantidad} {producto} registrada.\nGanancia: ${ganancia:.2f}")

# -------------------------------
# Interfaz gráfica (ventana)
# -------------------------------
ventana = tk.Tk()
ventana.title("Registrar Venta")
ventana.geometry("400x250")

# Producto
tk.Label(ventana, text="Producto:").pack()
combo_producto = ttk.Combobox(ventana, values=recetas_disponibles)
combo_producto.set("Seleccionar")
combo_producto.pack(pady=5)

# Cantidad
tk.Label(ventana, text="Cantidad vendida:").pack()
entry_cantidad = tk.Entry(ventana)
entry_cantidad.insert(0, "1")
entry_cantidad.pack(pady=5)

# Precio
tk.Label(ventana, text="Precio total de venta:").pack()
entry_precio = tk.Entry(ventana)
entry_precio.insert(0, "0")
entry_precio.pack(pady=5)

# Botón
tk.Button(ventana, text="Registrar Venta", command=registrar_venta).pack(pady=10)

ventana.mainloop()

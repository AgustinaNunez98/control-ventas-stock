import pandas as pd
from datetime import datetime

def actualizar_stock_con_compras(ingredientes_df, gastos_df):  #stock de comprar, actuliza el stock de ingredientes
    for idx, row in gastos_df.iterrows():
        producto = row['Producto']
        cantidad_comprada = row['Cantidad']
        
        # Ver si ya existe en Ingredientes
        mask = ingredientes_df['NOMBRE INGREDIENTE'] == producto
        
        if mask.any():
            # Sumar al stock actual
            ingredientes_df.loc[mask, 'STOCK ACTUAL'] += cantidad_comprada
        else:
            else:
    costo_unitario = row.get('Precio unitario', 0)
    costo_total = costo_unitario * cantidad_comprada

    nuevo_ingrediente = {
        'NOMBRE INGREDIENTE': producto,
        'UNIDAD DE MEDIDA': '',  # Podés completarlo luego
        'CANTIDAD COMPRADA': cantidad_comprada,
        'COSTO POR UNIDAD': costo_unitario,
        'COSTO TOTAL': costo_total,
        'PROVEEDOR': row.get('Proveedor', ''),
        'STOCK INICIAL': cantidad_comprada,
        'STOCK ACTUAL': cantidad_comprada,
        'ÚLTIMA COMPRA': row.get('Fecha', '')
    }

    ingredientes_df = pd.concat([ingredientes_df, pd.DataFrame([nuevo_ingrediente])], ignore_index=True)
    print(f"✅ Ingrediente nuevo agregado al stock: {producto}")

    
    return ingredientes_df


# Cargar datos del archivo
archivo = r"C:\Users\agust\OneDrive\Escritorio\Programa para Ketchinfy\Gastos y ganancias - copia.xlsx"

ingredientes_df = pd.read_excel(archivo, sheet_name="Ingredientes")
recetas_df = pd.read_excel(archivo, sheet_name="Recetas")
pedidos_df = pd.read_excel(archivo, sheet_name="Pedidos")
gastos_df = pd.read_excel(archivo, sheet_name="Gastos")

recetas_df = recetas_df.dropna(subset=["RECETA"]) #limpia recetas vacías
# ✅ Actualizar stock con las compras
ingredientes_df = actualizar_stock_con_compras(ingredientes_df, gastos_df)

# Función para vender un producto
def vender_producto(producto, cantidad_vendida):
    receta = recetas_df[recetas_df['RECETA'] == producto]
    
    if receta.empty:
        print("Producto no encontrado en las recetas.")
        return
    
    # Actualizar stock
    for idx, row in receta.iterrows():
        ingrediente = row['INGREDIENTE']
        cantidad_usada = row['CANTIDAD USADA'] * cantidad_vendida
        
        # Buscar ingrediente en stock
        mask = ingredientes_df['NOMBRE INGREDIENTE'] == ingrediente
        if not mask.any():
            print(f"Ingrediente {ingrediente} no encontrado en stock.")
            continue
        
        # Restar del stock
        ingredientes_df.loc[mask, 'STOCK ACTUAL'] -= cantidad_usada
        print(f"Descontado {cantidad_usada} de {ingrediente}")

    # Registrar en pedidos
    nuevo_pedido = {
        "Cliente": "Venta directa",  # podríamos personalizarlo después
        "Producto": producto,
        "Cantidad": cantidad_vendida,
        "Precio": 0,  # Opcionalmente se puede pedir el precio al usuario
        "Fecha": datetime.now().strftime("%Y-%m-%d"),
        "Aclaración": ""
    }
    pedidos_df.loc[len(pedidos_df)] = nuevo_pedido
    print(f"Venta de {producto} registrada.")

    # Guardar cambios
    with pd.ExcelWriter(archivo, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
        ingredientes_df.to_excel(writer, sheet_name='Ingredientes', index=False)
        pedidos_df.to_excel(writer, sheet_name='Pedidos', index=False)


def cancelar_ultima_venta():
    global ingredientes_df, pedidos_df  # Para poder modificar las variables de fuera

    if pedidos_df.empty:
        print("No hay ventas registradas.")
        return

    ultima_venta = pedidos_df.iloc[-1]
    producto = ultima_venta['Producto']
    cantidad = ultima_venta['Cantidad']

    receta = recetas_df[recetas_df['RECETA'] == producto]
    if receta.empty:
        print(f"No se encontró la receta de {producto} para revertir el stock.")
        return

    for _, row in receta.iterrows():
        ingrediente = row['INGREDIENTE']
        cantidad_usada = row['CANTIDAD USADA'] * cantidad

        mask = ingredientes_df['NOMBRE INGREDIENTE'] == ingrediente
        if mask.any():
            ingredientes_df.loc[mask, 'STOCK ACTUAL'] += cantidad_usada
            print(f"Reintegrado {cantidad_usada} de {ingrediente}")
        else:
            print(f"Ingrediente {ingrediente} no encontrado en stock")

    print(f"Cancelando venta de {producto} (cantidad: {cantidad})")
    pedidos_df.drop(pedidos_df.index[-1], inplace=True)

    with pd.ExcelWriter(archivo, mode='a', if_sheet_exists='overlay', engine='openpyxl') as writer:
        ingredientes_df.to_excel(writer, sheet_name='Ingredientes', index=False)
        pedidos_df.to_excel(writer, sheet_name='Pedidos', index=False)

    print("✅ Venta cancelada y stock actualizado.")

# --------------------
# MENÚ PRINCIPAL
# --------------------

productos_disponibles = recetas_df['RECETA'].unique()

while True:
    print("\n🛒 MENÚ DE VENTAS")
    print("Seleccioná el número del producto vendido:")
    
    for i, producto in enumerate(productos_disponibles):
        print(f"{i+1}. {producto}")
    
    print("0. Cancelar la última venta")
    print("-1. Salir")

    try:
        opcion = int(input("Ingresá tu opción: "))
    except ValueError:
        print("❌ Opción inválida. Ingresá un número.")
        continue

    if opcion == -1:
        print("Buena venta! A seguir así Ketchinfy. ¡Hasta la próxima venta!")
        break

    elif opcion == 0:
        cancelar_ultima_venta()
        continue

    elif 1 <= opcion <= len(productos_disponibles):
        producto_seleccionado = productos_disponibles[opcion - 1]
        try:
            cantidad = int(input("Cantidad vendida: "))
        except ValueError:
            print("❌ Ingresá un número válido para la cantidad.")
            continue

        vender_producto(producto_seleccionado, cantidad)
    
    else:
        print("❌ Opción no válida. Intentá nuevamente.")



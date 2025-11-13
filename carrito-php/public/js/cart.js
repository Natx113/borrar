const loadCart = () => {
    return JSON.parse(localStorage.getItem('cart')) || []

}

const saveCart = cart =>{
    localStorage.setItem('cart', JSON.stringify(cart))
}

const render = () => {
    const cart = loadCart()
    console.log('@@@ cart => ', cart)
    if (!cart.length){
        document.getElementById('cart').innerHTML = 
        '<div class="alert alert-info">Tu carrito esta vacio</div>'
        return
    }
    const rows = cart.map((i, idx) => `
        <tr>
            <td>${i.nombre}</td>
            <td>${i.precio.toFixed(2)}</td>
            <td>
                <input type="number" min="1" value="${i.qty}" class="form-control form-control-sm qty" data-idx="${idx}" style="width: 90px;">
            </td>
            <td>$ ${(i.qty * i.precio).toFixed(2)}</td>
            <td>
                <button class="btn btn-sm btn-danger remove">X</button>
            </td>
        </tr>
    `).join('')
    const total = cart.reduce((a, i) => a + i.qty * i.precio, 0)
    document.getElementById('cart').innerHTML = `
        <table class="table table-striped align-middle">
            <thead>
                <tr>
                    <th>Nombre</th>
                    <th>Precio</th>
                    <th>Cantidad</th>
                    <th>Subtotal</th>
                    <th>Quitar</th>
                </tr>
            </thead>
            <tbody>${rows}></tbody>
            <tfoot>
                <tr>
                    <th colspan="4" class="text-end">$ ${total.toFixed(2)}</th>
                    <th></th>
                </tr>
            </tfoot>
        </table>
        <button class="btn btn-success">Pagar</button>
    `
    document.querySelectorAll('.qty').forEach((inp) => {
        inp.onchange = () => {
            const cart = loadCart()
            cart[inp.dataset.idx].qty = Math.max(1, parseInt(inp.value || 1))
            saveCart(cart)
            render()
        }
    })
    document.querySelectorAll('.remove').forEach((btn) => {
        btn.onclick = () => {
            const cart = loadCart()
            cart.splice(btn.dataset.idx, 1)
            saveCart(cart)
            render()
        }
    })
}

render()
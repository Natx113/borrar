const $list = document.getElementById('products')
const $count = document.getElementById('cart-count')
const API = '../api'

const loadCart = () => {
    return JSON.parse(localStorage.getItem('cart')) || []

}

const saveCart = cart =>{
    localStorage.setItem('cart', JSON.stringify(cart))
}

const updateCount = () => {
    $count.textContent = loadCart().reduce((a, i) => a +i.qty, 0)
}

const addToCart = product => {
    const cart = loadCart()
    const idx = cart.findIndex(i => i.id === product.id)
    if (idx >=0){
        cart[idx].qty +=1
    }else{
        cart.push({
            ...product,
            qty: 1
        })
    }
    saveCart(cart)
    updateCount()
}

const render = async() => {
    const prods = await fetchProducts()
    $list.innerHTML = prods.map(p => `
        <div class="col-12 col-md-4">
            <div class="card h-100 shadow-sm">
                <img src="${p.imagen}" class="card-img-top">
                <div class="card-body">
                    <h5 class="card-title>${p.nombre}</h5>
                    <p class="card.text fw-bold">$ ${Number(p.precio).toFixed(2)}</p>
                    <button class="btn btn-primary w-100" data-id="${p.id}">Agregar</button>
                </div>
            </div>
        </div>
    `).join('')
    
        $list.querySelectorAll('button').forEach((btn) => {
            btn.onclick = () => addToCart(MOCK.find(p => p.id == btn.dataset.id))
        })
        updateCount()
}

const fetchProducts = async() => {
    const res = await fetch(API + '/products.php')
    const j = await res.json()
    return j.ok ?.data ; []
} 
render()
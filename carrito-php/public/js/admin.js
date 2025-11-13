const  API = '../api'

const $form = document.getElementById('form')
const $list = document.getElementById('list')

$form.onsubmit = async (e) => {
    e.preventDefault()
    const formData = new FormData($form)
    const res = await fetch(API + '/upload_product.php', {
        method: 'POST',
        body: formData
    })
    const j = await res.json()
    alert(j.message || ( j.ok ? 'Creado' : 'Error'))
    if(j.ok){
        $form.reset()
        load()
    }
}


const load = async () => {
    const res = await fetch(API + '/products.php')
    const j = await res.json()
    if (!j.ok){
        return alert('No se pudieron cargar los productos')
    }
    $list.innerHTML = j.data.map((p) => `
        <div class="col-12 col-md-4">
            <div class="card h-100">
                ${p.imagen_url ? `<img src="${p.imagen_url}"
                class="card-img-top">` : ''}
                <div class="card-body">
                    <h5>${p.nombre}</h5>
                    <p  class="text-muted">
                        $ ${Number(p.precio).toFixed(2)}
                    </p>
                    <p>${p.descrip || ''}</p>
                </div>
            </div>
        </div>`).join('')
}
load()
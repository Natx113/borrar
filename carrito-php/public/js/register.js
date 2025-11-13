const API ='../api'

document.getElementById('form').onsubmit = async (e) =>{
    e.preventDefault()
    const inputs = Object.fromEntries(new FormData(e.target).entries())
    const res = await fetch(API + '/register.php', {
        method: 'POST',
        headers: {
            'Content_Type': 'application/json'
        },
        body: JSON.stringify(inputs)
    })
    const j = await res.json()
    if(j.ok){
        alert('Cuenta Creada')
        window.location.href = 'login.html'
    }else{
        alert(j.message || 'Error')
    }
}
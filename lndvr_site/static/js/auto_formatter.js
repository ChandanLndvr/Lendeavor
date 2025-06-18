document.getElementById('ssn').addEventListener('input', function (e) {
        let x = e.target.value.replace(/\D/g, '').slice(0, 9);
        let formatted = x.replace(/^(\d{3})(\d{2})(\d{0,4})$/, '$1-$2-$3');
        e.target.value = formatted;
    });

    document.getElementById('taxid').addEventListener('input', function (e) {
        let x = e.target.value.replace(/\D/g, '').slice(0, 9);
        let formatted = x.replace(/^(\d{2})(\d{0,7})$/, '$1-$2');
        e.target.value = formatted;
    });
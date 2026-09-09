const provinceSelect = document.getElementById("id_province");
const citySelect = document.getElementById("id_city");
provinceSelect.addEventListener("change", function () {
    const provinceId = this.value;

    citySelect.innerHTML = '<option value="">---------</option>';

    if (!provinceId) {
        citySelect.disabled = true;
        return;
    }
    const url = getcitiesurl.replace("0", provinceId)
    fetch(url)
        .then(response => response.json())
        .then(cities => {
            cities.forEach(city => {
                const option = document.createElement("option");

                option.value = city.id;
                option.textContent = city.name;

                citySelect.appendChild(option);
            });

            citySelect.disabled = false;
        });
});
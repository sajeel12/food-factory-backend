function useFetchParts() {
    let isLoading = false;

    const fetchParts = async () => {
        try {
            isLoading = true;
            updateLoadingUI(true, 'fetch'); // Optional: Show loading UI

            const response = await fetch('/fetch-parts/', {
                method: 'GET',
                headers: { 'Content-Type': 'application/json' },
            });

            if (!response.ok) throw new Error('Failed to fetch parts');

            const parts = await response.json();
            updatePartsTable(parts);
        } catch (error) {
            console.error('Error fetching parts:', error);
        } finally {
            isLoading = false;
            updateLoadingUI(false, 'fetch'); // Optional: Hide loading UI
        }
    };

    return [fetchParts, () => isLoading];
}

// Helper function to update the parts table dynamically
function updatePartsTable(parts) {
    const tbody = document.querySelector('#parts_table tbody');
    tbody.innerHTML = ''; // Clear existing rows

    console.log(parts.parts)
    parts?.parts?.forEach((part) => {
        const row = `
            <tr class="table-hover odd:bg-white even:bg-gray-50">
                <th class="px-6 py-4 text-gray-900">${part.part_number}</th>
                <td class="px-6 py-4">${part.car_company_id}</td>
                <td class="px-6 py-4">${part.applicapibility}</td>
                <td class="px-6 py-4">${part.quantity_in_stock}</td>
                <td class="px-6 py-4">${part.supplier}</td>
                <td class="px-6 py-4">${part.rack_location}</td>
                <td class="px-6 py-4">${part.price_per_unit}</td>
                <td class="px-6 py-4">${part.tax}%</td>
                <td class="px-6 py-4">
                    <img onclick="openModal('delete-part-modal-${part.id}')"
                         class="cursor-pointer hover:scale-125"
                         width="25px" src="{% static 'svgs/trashicon.svg' %}" />
                </td>
            </tr>`;
        tbody.insertAdjacentHTML('beforeend', row);
    });
}

function useAddPart(fetchParts) {
    let isLoading = false;

    const addPart = async (event) => {
        event.preventDefault(); // Prevent form submission

        const form = document.getElementById('add_part_form');
        const formData = new FormData(form);
        const partData = Object.fromEntries(formData.entries());

        try {
            isLoading = true;
            updateLoadingUI(true, 'add'); // Optional: Show loading UI

            const response = await fetch('/api/parts/', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'X-CSRFToken': '{{ csrf_token }}',
                },
                body: JSON.stringify(partData),
            });

            if (!response.ok) throw new Error('Failed to add part');

            closeModal('add-part-modal');
            await fetchParts(); // Refresh parts list
        } catch (error) {
            console.error('Error adding part:', error);
        } finally {
            isLoading = false;
            updateLoadingUI(false, 'add'); // Optional: Hide loading UI
        }
    };

    return [addPart, () => isLoading];
}


function updateLoadingUI(isLoading, operation) {
    const loader = document.getElementById(`${operation}-loading-indicator`);
    loader.style.display = isLoading ? 'block' : 'none';
}


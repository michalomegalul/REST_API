import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';


const criticalProductIds = [123, 456, 789];

export default function() {
    for (let i = 0; i < criticalProductIds.length; i++) {
        const url = `http://localhost:5000/api/products/${criticalProductIds[i]}`; // Adjust to your product detail endpoint
        const response = http.get(url);

        check(response, {
            'status is 200': (r) => r.status === 200,
            // Add specific checks for the product detail page
        });
    }
    sleep(1);
}
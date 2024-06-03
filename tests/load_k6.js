import http from 'k6/http';
import { sleep } from 'k6';
import { check } from 'k6';
import { SharedArray } from 'k6/data';
import papaparse from 'https://jslib.k6.io/papaparse/5.1.1/index.js';

// Stress test of get favourites count endpoint
const max_vus = 100;
export let options = {
    stages: [
        { duration: '120s', target: max_vus }, // Ramp up to max_vus users over set duration
    ]
};
const productIds = new SharedArray('product IDs', function () {
    return papaparse.parse(open('./data.csv'), { header: true }).data.map(d => d.id);
  });

// const ids_for_one_virtual_user= user_ids.length / max_vus

export default function stressStestGetCount () {
    // each virtual user will have different user id section, -1 is because id is indexed from 1
    for (let i=0; i<productIds.length; i++) {
        const url = `http://localhost:5000/api/products/${productIds[i]}/offers`;
        const response = http.get(url);

        if (response.status !== 200) {
            console.error(`Error fetching offers for product ${productIds}:`, response.status, response.body);
        } else {
            try {
            console.log(`Offers for product ${productIds}:`, JSON.parse(response.body));
            } catch (e) {
            console.error(`Invalid JSON for product ${productIds}:`, e);
            }
        }
        // Check the response for k6 result output
        check(response, {
            'status is 200': (r) => r.status === 200,
            'no errors': (r) => JSON.parse(r.body).errors === undefined,
        });
        // Simulate a think time for each virtual user
    }

    sleep(1);
}

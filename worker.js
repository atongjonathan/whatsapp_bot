export default {
    async fetch(request, env, ctx) {

        let queryParams = get_parameters_dict()
        const reqUrl = new URL(request.url);
        let url = reqUrl.toString()
        let baseApiUrl = 'https://eu-west-2.aws.data.mongodb-api.com/app/data-kmyiqtw/endpoint/data/v1/action';


        async function get_access_token() {
            const tokenUrl = 'https://eu-west-2.aws.services.cloud.mongodb.com/api/client/v2.0/app/data-kmyiqtw/auth/providers/local-userpass/login';
            const tokenResponse = await fetch(tokenUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "username": "atongjonathan2@gmail.com",
                    "password": "selisrare"
                }),
            });

            const data = await tokenResponse.json()
            const apiKey = await data["access_token"]

            return apiKey
        }

        function get_parameters_dict() {
            const url = new URL(request.url);
            const queryParams = Object.fromEntries(url.searchParams.entries());
            const mongoQuery = {}
            for (const [key, value] of Object.entries(queryParams)) {
                mongoQuery[key] = value;
            }
            return queryParams
        }

        async function mongodb(url, type, mongoQuery, collection) {

            let apiKey = await get_access_token()
            let data = {
                "collection": collection,
                "database": "sgbot",
                "dataSource": "Cluster0",
            }
            data[type] = mongoQuery
            const response = await fetch(url, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Access-Control-Request-Headers': '*',
                    "Authorization": `Bearer ${apiKey}`,
                },
                body: JSON.stringify(data),
            });
            const responseBody = await response.json();
            return new Response(JSON.stringify({ response: responseBody }, null, 2), {
                headers: { 'Content-Type': 'application/json' },
            });
        }


        if (request.method == 'GET') {
            const mongoQuery = get_parameters_dict()
            baseApiUrl += "/findOne"
            let collection = url.includes("whatsapp") ? "whatsapp" : "songs"
            let type = "document"
            await mongodb(baseApiUrl, type, mongoQuery, collection)


        }
        if (request.method == 'POST') {

            // Extract the URL and query parameters from the request
            const mongoQuery = request.json()

            baseApiUrl += "/insertOne";
            let collection = url.includes("whatsapp") ? "whatsapp" : "songs";
            let type = "document"

            await mongodb(baseApiUrl, type, mongoQuery, collection)
        }

        if (request.method == 'DELETE') {
            const mongoQuery = request.json()
            let type = "filter"
            baseApiUrl += "/deleteOne";
            let collection = url.includes("whatsapp") ? "whatsapp" : "songs";

            await mongodb(baseApiUrl, type, mongoQuery, collection)
        }

        if (request.method == 'PUT') {
            const apiUrl = 'http://ec2-3-94-170-231.compute-1.amazonaws.com/song';

            const response = await fetch(apiUrl, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    'Authorization': 'Basic  am9uYTpzZWxpc3JhcmU=',
                },
                body: JSON.stringify(queryParams),
            });

            // Check if the response from the API is OK
            if (!response.ok) {
                const errorText = await response.text(); // Get the error message from the response
                return new Response(errorText, { status: response.status });
            }

            // Parse and return the successful response
            const responseBody = await response.json();
            return new Response(JSON.stringify({ response: responseBody }, null, 2), {
                headers: { 'Content-Type': 'application/json' },
            });
        }
    },
};

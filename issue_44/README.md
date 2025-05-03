# Charity Navigator GraphQL API Guide

This README provides guidance on how to use the Charity Navigator GraphQL API to query nonprofit data and outlines the benefits of using GraphQL over REST.

---

## 🚀 Why GraphQL?

GraphQL offers several advantages over traditional REST APIs:

- **Single Endpoint**: Unlike REST where each resource requires a different endpoint, GraphQL uses a single `/graphql` endpoint for all queries and mutations.
- **Flexible Queries**: Clients can request exactly the data they need — no more, no less.
- **Reduced Overfetching**: Avoid unnecessary data transmission by querying only specific fields.
- **Schema Introspection**: Easily explore available fields and types with introspection queries.
- **Efficient Pagination**: Use `from` and `result_size` in queries to paginate large datasets efficiently.

---

## 📘 About the Charity Navigator GraphQL API

The Charity Navigator GraphQL API allows developers to search for and retrieve detailed information about nonprofits. Key query types include:

- `publicSearchFaceted`: Faceted search over nonprofits with filtering and pagination.
- `bulkNonprofits`: Retrieve multiple nonprofits based on filter criteria.
- `nonprofits`: Fetch nonprofits by EIN.
- `rating`, `alerts`, `taxReturns`: Get additional data for a specific nonprofit.

---

## 🧾 Sample GraphQL Query

```graphql
{
  publicSearchFaceted(
      term: "",
          states: [],
              sizes: [],
                  causes: [],
                      ratings: [],
                          c3: false,
                              result_size: 10,
                                  from: 0,
                                      beacons: [],
                                          advisories: [],
                                              order_by: "relevance"
                                                ) {
                                                    results {
                                                          ein
                                                                name
                                                                      mission
                                                                            organization_url
                                                                                  charity_navigator_url
                                                                                        encompass_score
                                                                                              encompass_star_rating
                                                                                                    encompass_publication_date
                                                                                                          cause
                                                                                                                street
                                                                                                                      street2
                                                                                                                            city
                                                                                                                                  state
                                                                                                                                        zip
                                                                                                                                              country
                                                                                                                                                    highest_level_advisory
                                                                                                                                                          highest_level_alert
                                                                                                                                                                encompass_rating_id
                                                                                                                                                                      acronym
                                                                                                                                                                          }
                                                                                                                                                                              total_results
                                                                                                                                                                                }
                                                                                                                                                                                }


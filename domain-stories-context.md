# Domain Storytelling – Taxonomy, Relationships, and Schema Context

This document summarizes the complete **Domain Storytelling Taxonomy** and its **relationships**, along with the schema design principles and conventions captured in the `domain-stories-schema.yaml` specification.

---

## 1. Overview

**Domain Storytelling** is a collaborative Domain-Driven Design (DDD) technique used to capture and visualize business processes as stories involving **actors**, **activities**, and **work objects**.  
The purpose of this taxonomy and schema is to formalize those concepts into structured, machine-readable artifacts that can be validated and reasoned about by LLMs or software systems.

---

## 2. Core Taxonomy

| Concept | Definition | Examples |
|----------|-------------|----------|
| **Actor** | A person, system, or role participating in the story. | Customer, Cashier, Payment System |
| **Activity** | An action performed by one or more actors that changes system state or produces a result. | Place Order, Approve Loan |
| **Work Object** | Domain artifact manipulated or produced by activities. Typically an Entity or Value Object in DDD. | Order, Invoice, Contract |
| **Event** | A fact representing something that *has happened* in the domain. | Order Created, Payment Received |
| **Rule** | A condition or constraint governing behavior. | Only registered users may place orders |
| **Interaction** | The flow of actions and events among actors. | Customer places order → System confirms → Warehouse ships |
| **Command** | An instruction expressing intent, usually from an actor to the system. | Submit Order, Cancel Subscription |
| **Query** | A request for information without state change. | Check Order Status, Get Invoice History |
| **Policy** | A reactive rule linking events to commands (“whenever X happens, do Y”). | After Order Created, send confirmation email |
| **Aggregate** | Cluster of entities treated as one unit for data consistency. | OrderAggregate (Order + LineItems) |
| **Repository** | Abstraction for persisting and retrieving aggregates. | OrderRepository |
| **Application Service** | Coordinates commands, queries, and repository interactions. | OrderService |
| **Domain Service** | Contains domain logic that doesn’t belong to a single aggregate. | PricingService |
| **Read Model** | Optimized projection for queries and reporting. | OrderSummaryView |

---

## 3. Relationships and Causal Flow

The taxonomy reflects a **causal chain** of intent, action, and outcome.

### High-Level Flow

1. **Actors** initiate **Commands** or **Queries**.  
2. **Commands** trigger **Activities** that manipulate **Work Objects** or **Aggregates**.  
3. **Activities** produce **Events** describing what happened.  
4. **Events** may trigger **Policies** that issue new **Commands**, creating feedback loops.  
5. **Repositories** and **Application Services** persist or coordinate the above interactions.  
6. **Domain Services** encapsulate domain-specific logic used by commands, policies, or activities.  
7. **Queries** fetch **Read Models** for information retrieval.

### Structural Relationships

| From | To | Type | Description |
|------|----|------|--------------|
| Actor | Command / Query | Initiates | Actor issues an intent. |
| Command | Aggregate | Targets | Command modifies the aggregate root. |
| Command | Activity | Causes | Activity executes command logic. |
| Activity | Work Object | Uses / Produces | Activities read/write work objects. |
| Activity | Event | Emits | Activities produce domain events. |
| Event | Policy | Triggers | Policies react to events. |
| Policy | Command | Issues | Policies create new commands as reactions. |
| Command | Application Service | Invokes | Commands are processed through services. |
| Application Service | Repository | Uses | Services persist or load aggregates. |
| Domain Service | Aggregate / Work Object | Operates On | Encapsulates reusable logic. |
| Query | Read Model | Returns | Queries retrieve read models. |

---

## 4. Schema Conventions

The `domain-stories-schema.yaml` formalizes this taxonomy using **JSON Schema (YAML form)** with the following conventions:

### ID Format

Each object type has a strict ID pattern (lowercase, snake_case):

| Object Type | Prefix | Example |
|--------------|---------|----------|
| Domain Story | `dst_` | `dst_checkout_process` |
| Actor | `act_` | `act_customer` |
| Command | `cmd_` | `cmd_submit_order` |
| Query | `qry_` | `qry_get_order_status` |
| Event | `evt_` | `evt_order_created` |
| Policy | `pol_` | `pol_notify_customer` |
| Aggregate | `agg_` | `agg_order` |
| Repository | `repo_` | `repo_order_repository` |
| Application Service | `svc_app_` | `svc_app_order` |
| Domain Service | `svc_dom_` | `svc_dom_pricing` |
| Work Object | `wobj_` | `wobj_invoice` |
| Activity | `actv_` | `actv_process_payment` |
| Read Model | `rmdl_` | `rmdl_order_summary` |
| Rule | `rle_` | `rle_max_order_amount` |

### Structural Enforcement via `$defs`

Each entity in the schema references others using `$ref` rather than inline pattern duplication.  
For example:

```yaml
actor_ids:
  type: array
  items:
    $ref: "#/$defs/ActId"
```

This ensures consistency across all references.

### Validation Rules

- All objects use **`additionalProperties: false`** to enforce strict typing.  
- Cross-references (e.g., a `Command` referencing `ActId` or `AggId`) are validated structurally.  
- JSON Schema can’t ensure actual *existence* of referenced IDs, but a secondary validator can.  
- Arrays like `actors`, `commands`, `queries`, and `events` support multiple instances for complex stories.  
- Relationships such as `caused_by`, `invokes_app_services`, `emits_events`, and `policies_triggered` express causal structure explicitly.

---

## 5. Example Narrative Mapping

### Example Story: Order Processing

1. `act_customer` issues `cmd_submit_order` targeting `agg_order`.
2. `cmd_submit_order` triggers `actv_validate_and_save_order`.
3. `actv_validate_and_save_order` produces `evt_order_created`.
4. `evt_order_created` triggers `pol_send_confirmation_email`, which issues `cmd_notify_customer`.
5. `qry_get_order_status` retrieves `rmdl_order_summary`.

This creates a traceable narrative flow of **intent → action → event → reaction**.

---

## 6. Integration with Adjacent DDD Practices

| Practice | Relation |
|-----------|-----------|
| **Event Storming** | Event Storming complements Domain Storytelling by surfacing events, commands, and policies visually before schema formalization. |
| **Ubiquitous Language** | All entity names should align with a shared domain language to ensure consistent interpretation. |
| **Bounded Contexts** | Each Domain Story belongs to a bounded context; IDs can be namespaced accordingly. |
| **Aggregates and Repositories** | Provide transactional consistency boundaries for Work Objects. |
| **Application & Domain Services** | Implement orchestration and pure domain logic respectively. |

---

## 7. Schema Generation Notes

- Implemented with **JSON Schema Draft 2020-12** in YAML format.  
- File name: `domain-stories-schema.yaml`  
- Includes `$defs` for all core entity types and reusable objects (e.g., `Attribute`, `Parameter`, `Operation`).  
- Suitable for validation, generation, and reasoning by LLMs.

---

## 8. Summary

This taxonomy and schema provide a unified model for representing **Domain Stories** as structured DDD artifacts.  
It integrates narrative-driven discovery (Domain Storytelling) with formal domain modeling (Aggregates, Commands, Events) to bridge human understanding and machine reasoning.

---

**Recommended Next Steps**  
- Use this document and schema as grounding context for an LLM that generates or validates YAML domain stories.  
- Extend it with custom validation logic for referential integrity.  
- Integrate with Event Storming or DDD modeling workflows to capture evolving domain knowledge.

---

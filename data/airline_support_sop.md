# Airline Cargo Support SOP

## AWB Not Visible After Message Upload

An AWB may not be visible in the cargo system if the shipment message failed validation, mandatory message segments are missing, or the booking has not been synchronized from the external cargo management system. Support users should first check message processing logs, then validate whether the AWB number exists in the booking tables.

## Mandatory Shipment Message Segments

Shipment messages must contain valid AWB, SHP, CNE, RTD, and AGT segments. Missing mandatory segments can cause the message to be rejected and may prevent AWB creation in the cargo system.

## Customs Information Segment Validation

The customs information segment contains regulatory and customs-related information. If destination customs data is required but missing, the shipment message may fail validation. Support users should check whether the segment contains the required country code, information identifier, and customs details.

## AWB Delay Reason

AWB delay can happen due to customs hold, flight offload, capacity constraint, late acceptance, missing shipment documentation, or failed message processing. Support users should check shipment status, flight movement, booking update logs, and shipment message history.

## House Shipment Validation

House shipment messages contain house airway bill information. Missing house shipper, consignee, or goods description can cause validation errors. House shipment validation issues may affect consolidation visibility but do not always block master AWB creation.

## Booking Request Validation

Booking request messages are used for cargo booking requests. A booking request may be rejected if the requested flight is closed, capacity is unavailable, or mandatory booking details are missing.

## Escalation

If the issue cannot be confirmed from SOPs or logs, escalate to the airline cargo support team with AWB number, flight number, timestamp, error message, and affected environment.
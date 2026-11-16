import type { Effect } from "effect";

import type { PolarClient, PolarRequestError } from "../../PolarClient";

import { request } from "../../PolarClient";
import * as Errors from "../errors";
import * as Models from "../models";

/**
 * Get metrics about your orders and subscriptions.
 *
 * Currency values are output in cents.
 *
 * **Scopes**: `metrics:read`
 */
export const get = (query: {
  readonly start_date: string;
  readonly end_date: string;
  readonly timezone?: Models.Timezone;
  readonly interval: Models.TimeInterval;
  readonly organization_id?: string | ReadonlyArray<string> | null;
  readonly product_id?: string | ReadonlyArray<string> | null;
  readonly billing_type?:
    | Models.ProductBillingType
    | ReadonlyArray<Models.ProductBillingType>
    | null;
  readonly customer_id?: string | ReadonlyArray<string> | null;
  readonly metrics?: ReadonlyArray<string> | null;
}): Effect.Effect<
  Models.MetricsResponse,
  Errors.MetricsGetErrors | PolarRequestError,
  PolarClient
> =>
  request({
    method: "GET",
    path: "/v1/metrics/",
    query,
    success: Models.MetricsResponse,
    errors: { 422: [[Models.HTTPValidationError, Errors.MetricsGetHTTPValidationError]] },
  });

/**
 * Get the interval limits for the metrics endpoint.
 *
 * **Scopes**: `metrics:read`
 */
export const limits = (): Effect.Effect<Models.MetricsLimits, PolarRequestError, PolarClient> =>
  request({ method: "GET", path: "/v1/metrics/limits", success: Models.MetricsLimits });

/** @odoo-module **/

import { registry } from "@web/core/registry";
import { standardFieldProps } from "@web/views/fields/standard_field_props";
import { Component, useRef, useState } from "@odoo/owl";

/**
 * Invoice Limit Slider
 *
 * A draggable slider widget for monetary/float/integer fields.
 * While dragging, the visual position is tracked in local component
 * state only (no ORM writes), so the handle follows the mouse instantly
 * with no lag. The record is updated once, on pointer release, which
 * keeps expensive recomputes (onchange, related field refresh, etc.)
 * from firing on every mouse-move event.
 */
export class InvoiceLimitSlider extends Component {
    static template = "sale_invoice_limit.InvoiceLimitSlider";
    static props = {
        ...standardFieldProps,
        maxField: { type: String, optional: true },
    };

    setup() {
        this.trackRef = useRef("track");
        this.state = useState({
            dragging: false,
            previewValue: 0,
        });
    }

    get max() {
        const maxFieldName = this.props.maxField || "amount_total";
        const maxVal = this.props.record.data[maxFieldName];
        return maxVal && maxVal > 0 ? maxVal : 1000;
    }

    get value() {
        if (this.state.dragging) {
            return this.state.previewValue;
        }
        return this.props.record.data[this.props.name] || 0;
    }

    get percent() {
        if (!this.max) {
            return 0;
        }
        const pct = (this.value / this.max) * 100;
        return Math.min(100, Math.max(0, pct));
    }

    get ticks() {
        const steps = 5;
        const ticks = [];
        for (let i = 0; i <= steps; i++) {
            ticks.push(Math.round((this.max / steps) * i));
        }
        return ticks;
    }

    formatValue(val) {
        return new Intl.NumberFormat(undefined, {
            maximumFractionDigits: 0,
        }).format(Math.round(val || 0));
    }

    valueFromEvent(ev) {
        const rect = this.trackRef.el.getBoundingClientRect();
        let ratio = (ev.clientX - rect.left) / rect.width;
        ratio = Math.min(1, Math.max(0, ratio));
        return Math.round(ratio * this.max);
    }

    onPointerDown(ev) {
        if (!this.trackRef.el) {
            return;
        }
        this.state.dragging = true;
        this.state.previewValue = this.valueFromEvent(ev);

        const onMove = (e) => {
            this.state.previewValue = this.valueFromEvent(e);
        };
        const onUp = async () => {
            window.removeEventListener("pointermove", onMove);
            window.removeEventListener("pointerup", onUp);
            const finalValue = this.state.previewValue;
            this.state.dragging = false;
            await this.props.record.update({ [this.props.name]: finalValue });
        };

        window.addEventListener("pointermove", onMove);
        window.addEventListener("pointerup", onUp);
    }
}

registry.category("fields").add("invoice_limit_slider", {
    component: InvoiceLimitSlider,
    supportedTypes: ["monetary", "float", "integer"],
    extractProps: ({ options }) => ({
        maxField: options.max_field,
    }),
});

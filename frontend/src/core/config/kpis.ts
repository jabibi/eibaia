export interface KpiDefinition {
  id: string;
  titleKey: string;
  module: string;
  to: string;
  variant?: "warning" | "danger" | "featured";
  permission?: string;
}

export const KPI_REGISTRY: KpiDefinition[] = [
  {
    id: "finance_balance",
    titleKey: "finance.kpi.balance",
    module: "finance",
    to: "/finance/transactions",
    variant: "featured",
  },
  {
    id: "finance_cash_month",
    titleKey: "finance.kpi.cashMonth",
    module: "finance",
    to: "/finance/transactions?filter=cash",
  },
  {
    id: "finance_card_month",
    titleKey: "finance.kpi.cardMonth",
    module: "finance",
    to: "/finance/transactions?filter=card",
  },
  {
    id: "finance_drafts",
    titleKey: "finance.kpi.drafts",
    module: "finance",
    to: "/finance/transactions?filter=review",
    variant: "warning",
    permission: "CASHBOX_MANAGE",
  },
  {
    id: "finance_labels",
    titleKey: "finance.kpi.labels",
    module: "finance",
    to: "/finance/labels",
    permission: "CASHBOX_MANAGE",
  },
  {
    id: "finance_reports",
    titleKey: "finance.kpi.reports",
    module: "finance",
    to: "/finance/reports",
    permission: "CASHBOX_MANAGE",
  },
  {
    id: "settings_users",
    titleKey: "settings.cards.users",
    module: "settings",
    to: "/settings/users",
    permission: "SYSTEM_ADMIN",
  },
  {
    id: "settings_reset",
    titleKey: "settings.cards.reset",
    module: "settings",
    to: "/settings/reset",
    variant: "danger",
    permission: "SYSTEM_ADMIN",
  },
];

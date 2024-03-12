defmodule LinkLangClassifier.Repo do
  use Ecto.Repo,
    otp_app: :link_lang_classifier,
    adapter: Ecto.Adapters.Postgres
end

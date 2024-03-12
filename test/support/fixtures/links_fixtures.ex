defmodule LinkLangClassifier.LinksFixtures do
  @moduledoc """
  This module defines test helpers for creating
  entities via the `LinkLangClassifier.Links` context.
  """

  @doc """
  Generate a link.
  """
  def link_fixture(attrs \\ %{}) do
    {:ok, link} =
      attrs
      |> Enum.into(%{
        category: 42,
        classified_by: 42,
        url: "some url"
      })
      |> LinkLangClassifier.Links.create_link()

    link
  end
end

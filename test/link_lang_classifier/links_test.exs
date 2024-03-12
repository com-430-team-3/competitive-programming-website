defmodule LinkLangClassifier.LinksTest do
  use LinkLangClassifier.DataCase

  alias LinkLangClassifier.Links

  describe "links" do
    alias LinkLangClassifier.Links.Link

    import LinkLangClassifier.LinksFixtures

    @invalid_attrs %{category: nil, classified_by: nil, url: nil}

    test "list_links/0 returns all links" do
      link = link_fixture()
      assert Links.list_links() == [link]
    end

    test "get_link!/1 returns the link with given id" do
      link = link_fixture()
      assert Links.get_link!(link.id) == link
    end

    test "create_link/1 with valid data creates a link" do
      valid_attrs = %{category: 42, classified_by: 42, url: "some url"}

      assert {:ok, %Link{} = link} = Links.create_link(valid_attrs)
      assert link.category == 42
      assert link.classified_by == 42
      assert link.url == "some url"
    end

    test "create_link/1 with invalid data returns error changeset" do
      assert {:error, %Ecto.Changeset{}} = Links.create_link(@invalid_attrs)
    end

    test "update_link/2 with valid data updates the link" do
      link = link_fixture()
      update_attrs = %{category: 43, classified_by: 43, url: "some updated url"}

      assert {:ok, %Link{} = link} = Links.update_link(link, update_attrs)
      assert link.category == 43
      assert link.classified_by == 43
      assert link.url == "some updated url"
    end

    test "update_link/2 with invalid data returns error changeset" do
      link = link_fixture()
      assert {:error, %Ecto.Changeset{}} = Links.update_link(link, @invalid_attrs)
      assert link == Links.get_link!(link.id)
    end

    test "delete_link/1 deletes the link" do
      link = link_fixture()
      assert {:ok, %Link{}} = Links.delete_link(link)
      assert_raise Ecto.NoResultsError, fn -> Links.get_link!(link.id) end
    end

    test "change_link/1 returns a link changeset" do
      link = link_fixture()
      assert %Ecto.Changeset{} = Links.change_link(link)
    end
  end
end

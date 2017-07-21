USE [SobekDB]
GO
/****** Object:  StoredProcedure [dbo].[SobekCM_Metadata_Exact_Search_Paged2]    Script Date: 07/20/2017 15:24:21 ******/
SET ANSI_NULLS ON
GO
SET QUOTED_IDENTIFIER ON
GO


-- Perform an EXACT match type of search against one field of metadata
ALTER PROCEDURE [dbo].[SobekCM_Metadata_Exact_Search_Paged2]
    @term1 nvarchar(512),
    @field1 int,
    @include_private bit,
    @aggregationcode varchar(20),
    @daterange_start bigint,
    @daterange_end bigint,
    @pagesize int,
    @pagenumber int,
    @sort int,
    @minpagelookahead int,
    @maxpagelookahead int,
    @lookahead_factor float,
    @include_facets bit,
    @facettype1 smallint,
    @facettype2 smallint,
    @facettype3 smallint,
    @facettype4 smallint,
    @facettype5 smallint,
    @facettype6 smallint,
    @facettype7 smallint,
    @facettype8 smallint,
    @total_items int output,
    @total_titles int output,
    @all_collections_items int output,
    @all_collections_titles int output
AS
BEGIN

    -- No need to perform any locks here, especially given the possible
    -- length of this search
    SET TRANSACTION ISOLATION LEVEL READ UNCOMMITTED;
    SET NOCOUNT ON;

    -- Create the temporary table variable first
    -- Create the temporary table variable to hold all the item id's
    create table #TEMP_ITEMS ( ItemID int primary key, fk_TitleID int, Hit_Count int, SortDate bigint );

    -- Determine the start and end rows
    declare @rowstart int;
    declare @rowend int;
    set @rowstart = (@pagesize * ( @pagenumber - 1 )) + 1;
    set @rowend = @rowstart + @pagesize - 1;

    -- Set value for filtering privates
    declare @lower_mask int;
    set @lower_mask = 0;
    if ( @include_private = 'true' )
    begin
        set @lower_mask = -256;
    end;

    -- Determine the aggregationid
    declare @aggregationid int;
    set @aggregationid = coalesce(( select AggregationID from SobekCM_Item_Aggregation where Code=@aggregationcode ), -1);

    -- Get the sql which will be used to return the aggregation-specific display values for all the items in this page of results
    declare @item_display_sql nvarchar(max);
    if ( @aggregationid < 0 )
    begin
        select @item_display_sql=coalesce(Browse_Results_Display_SQL, 'select S.ItemID, S.Publication_Date, S.Creator, S.[Publisher.Display], S.Format, S.Edition, S.Material, S.Measurements, S.Style_Period, S.Technique, S.[Subjects.Display], S.Source_Institution, S.Donor from SobekCM_Metadata_Basic_Search_Table S, @itemtable T where S.ItemID = T.ItemID order by T.RowNumber;')
        from SobekCM_Item_Aggregation
        where Code='all';
    end
    else
    begin
        select @item_display_sql=coalesce(Browse_Results_Display_SQL, 'select S.ItemID, S.Publication_Date, S.Creator, S.[Publisher.Display], S.Format, S.Edition, S.Material, S.Measurements, S.Style_Period, S.Technique, S.[Subjects.Display], S.Source_Institution, S.Donor from SobekCM_Metadata_Basic_Search_Table S, @itemtable T where S.ItemID = T.ItemID order by T.RowNumber;')
        from SobekCM_Item_Aggregation
        where AggregationID=@aggregationid;
    end;

    -- Determine the first 100 of the search term
    declare @term_start nvarchar(100);
    set @term_start = SUBSTRING(@term1, 1, 100);

    -- Perform the actual metadata search differently, depending on whether an aggregation was
    -- included to limit this search
    if (( @daterange_end < 0 ) and ( @daterange_start < 0 ))
    begin
        if ( @aggregationid > 0 )
        begin
            insert into #TEMP_ITEMS ( ItemID, fk_TitleID, SortDate )
            select I.ItemID, I.GroupID, SortDate=isnull( I.SortDate,-1)
            from SobekCM_Item AS I inner join
                 SobekCM_Item_Aggregation_Item_Link AS CL ON CL.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Link ML on ML.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Search_Table M ON M.MetadataID = ML.MetadataID and MetadataTypeID = @field1 and M.MetadataValueStart = @term_start and M.MetadataValue = @term1
            where ( I.Deleted = 'false' )
              and ( CL.AggregationID = @aggregationid )
              and ( I.IP_Restriction_Mask >= @lower_mask )
              and ( I.Dark = 'false' );
        end
        else
        begin
            insert into #TEMP_ITEMS ( ItemID, fk_TitleID, SortDate )
            select I.ItemID, I.GroupID, SortDate=isnull( I.SortDate,-1)
            from SobekCM_Item AS I inner join
                 SobekCM_Metadata_Unique_Link ML on ML.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Search_Table M ON M.MetadataID = ML.MetadataID and MetadataTypeID = @field1 and M.MetadataValueStart = @term_start and M.MetadataValue = @term1
            where ( I.Deleted = 'false' )
              and ( I.IP_Restriction_Mask >= @lower_mask )
              and ( I.IncludeInAll = 'true' )
              and ( I.Dark = 'false' );
        end;
    end
    else
    begin
        if ( @aggregationid > 0 )
        begin
            insert into #TEMP_ITEMS ( ItemID, fk_TitleID, SortDate )
            select I.ItemID, I.GroupID, SortDate=isnull( I.SortDate,-1)
            from SobekCM_Item AS I inner join
                 SobekCM_Item_Aggregation_Item_Link AS CL ON CL.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Link ML on ML.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Search_Table M ON M.MetadataID = ML.MetadataID and MetadataTypeID = @field1 and M.MetadataValueStart = @term_start and M.MetadataValue = @term1
            where ( I.Deleted = 'false' )
              and ( CL.AggregationID = @aggregationid )
              and ( I.IP_Restriction_Mask >= @lower_mask )
              and ( I.Dark = 'false' )
              and ( I.SortDate >= @daterange_start )
              and ( I.SortDate <= @daterange_end );
        end
        else
        begin
            insert into #TEMP_ITEMS ( ItemID, fk_TitleID, SortDate )
            select I.ItemID, I.GroupID, SortDate=isnull( I.SortDate,-1)
            from SobekCM_Item AS I inner join
                 SobekCM_Metadata_Unique_Link ML on ML.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Search_Table M ON M.MetadataID = ML.MetadataID
                 and MetadataTypeID = @field1 and M.MetadataValueStart = @term_start and M.MetadataValue = @term1
            where ( I.Deleted = 'false' )
              and ( I.IP_Restriction_Mask >= @lower_mask )
              and ( I.IncludeInAll = 'true' )
              and ( I.Dark = 'false' )
              and ( I.SortDate >= @daterange_start )
              and ( I.SortDate <= @daterange_end );
        end;
    end;

    -- If there were no results at all, check the count in the entire library
    if ( ( select COUNT(*) from #TEMP_ITEMS ) = 0 )
    begin
        -- Set the items and titles correctly
        set @total_items = 0;
        set @total_titles = 0;

        -- If there was an aggregation id, just return the counts for the whole library
        if ( @aggregationid > 0 )
        begin
            -- Get all items in the entire library then
            insert into #TEMP_ITEMS ( ItemID, fk_TitleID, SortDate )
            select I.ItemID, I.GroupID, SortDate=isnull( I.SortDate,-1)
            from SobekCM_Item AS I inner join
                 SobekCM_Metadata_Unique_Link ML on ML.ItemID = I.ItemID inner join
                 SobekCM_Metadata_Unique_Search_Table M ON M.MetadataID = ML.MetadataID
                 and MetadataTypeID = @field1 and M.MetadataValueStart = @term_start and M.MetadataValue = @term1
            where ( I.Deleted = 'false' )
              and ( I.IP_Restriction_Mask >= @lower_mask )
              and ( I.IncludeInAll = 'true' );

            -- Return these counts
            select @all_collections_items=COUNT(*), @all_collections_titles=COUNT(distinct fk_TitleID)
            from #TEMP_ITEMS;
        end;
    end
    else
    begin
        -- Create the temporary item table variable for paging purposes
        declare @TEMP_PAGED_ITEMS TempPagedItemsTableType;

        -- There are essentially two major paths of execution, depending on whether this should
        -- be grouped as items within the page requested titles ( sorting by title or the basic
        -- sorting by rank, which ranks this way ) or whether each item should be
        -- returned by itself, such as sorting by individual publication dates, etc..
        if ( @sort < 10 )
        begin
            -- create the temporary title table definition
            declare @TEMP_TITLES table ( TitleID int, BibID varchar(10), RowNumber int);

            -- Get the total counts
            select @total_items=COUNT(*), @total_titles=COUNT(distinct fk_TitleID)
            from #TEMP_ITEMS;

            -- Now, calculate the actual ending row, based on the ration, page information,
            -- and the lookahead factor
            if (( @total_items > 0 ) and ( @total_titles > 0 ))
            begin
                -- Compute equation to determine possible page value ( max - log(factor, (items/title)/2))
                declare @computed_value int;
                select @computed_value = (@maxpagelookahead - CEILING( LOG10( ((cast(@total_items as float)) / (cast(@total_titles as float)))/@lookahead_factor)));

                -- Compute the minimum value.  This cannot be less than @minpagelookahead.
                declare @floored_value int;
                select @floored_value = 0.5 * ((@computed_value + @minpagelookahead) + ABS(@computed_value - @minpagelookahead));

                -- Compute the maximum value.  This cannot be more than @maxpagelookahead.
                declare @actual_pages int;
                select @actual_pages = 0.5 * ((@floored_value + @maxpagelookahead) - ABS(@floored_value - @maxpagelookahead));

                -- Set the final row again then
                set @rowend = @rowstart + ( @pagesize * @actual_pages ) - 1;
            end;

            -- Create saved select across titles for row numbers for selecting correct page(s) of results
            with TITLES_SELECT AS
                (    select GroupID, G.BibID,
                        ROW_NUMBER() OVER (order by case when @sort=0 THEN G.SortTitle end ASC,
                                                    case when @sort=1 THEN G.SortTitle end ASC,
                                                    case when @sort=2 THEN BibID end ASC,
                                                    case when @sort=3 THEN BibID end DESC) as RowNumber
                    from #TEMP_ITEMS I, SobekCM_Item_Group G
                    where I.fk_TitleID = G.GroupID
                    group by G.GroupID, G.BibID, G.SortTitle )

            -- Insert the correct rows into the temp title table
            insert into @TEMP_TITLES ( TitleID, BibID, RowNumber )
            select GroupID, BibID, RowNumber
            from TITLES_SELECT
            where RowNumber >= @rowstart
              and RowNumber <= @rowend;

            -- Return the title information for this page of results
            select RowNumber as TitleID, T.BibID, G.GroupTitle, G.ALEPH_Number as OPAC_Number, G.OCLC_Number, isnull(G.GroupThumbnail,'') as GroupThumbnail, G.[Type], isnull(G.Primary_Identifier_Type,'') as Primary_Identifier_Type, isnull(G.Primary_Identifier, '') as Primary_Identifier
            from @TEMP_TITLES T, SobekCM_Item_Group G
            where ( T.TitleID = G.GroupID )
            order by RowNumber ASC;

            -- Get the item id's for the items related to these titles
            insert into @TEMP_PAGED_ITEMS
            select ItemID, RowNumber
            from @TEMP_TITLES T, SobekCM_Item I
            where ( T.TitleID = I.GroupID );

            -- Return the basic system required item information for this page of results
            select T.RowNumber as fk_TitleID, I.ItemID, VID, Title, IP_Restriction_Mask, coalesce(I.MainThumbnail,'') as MainThumbnail
            , coalesce(I.Level1_Index, -1) as Level1_Index, coalesce(I.Level1_Text,'') as Level1_Text
            , coalesce(I.Level2_Index, -1) as Level2_Index, coalesce(I.Level2_Text,'') as Level2_Text, coalesce(I.Level3_Index,-1) as Level3_Index
            , coalesce(I.Level3_Text,'') as Level3_Text, isnull(I.PubDate,'') as PubDate, I.[PageCount], coalesce(I.Link,'') as Link
            , coalesce( Spatial_KML, '') as Spatial_KML, coalesce(COinS_OpenURL, '') as COinS_OpenURL
            from SobekCM_Item I, @TEMP_PAGED_ITEMS T
            where ( T.ItemID = I.ItemID )
            order by T.RowNumber, Level1_Index, Level2_Index, Level3_Index;

            -- Return the aggregation-specific display values for all the items in this page of results
            execute sp_Executesql @item_display_sql, N' @itemtable TempPagedItemsTableType READONLY', @TEMP_PAGED_ITEMS;
        end
        else
        begin
            -- Since these sorts make each item paired with a single title row,
            -- number of items and titles are equal
            select @total_items=COUNT(*), @total_titles=COUNT(*)
            from #TEMP_ITEMS;

            -- In addition, always return the max lookahead pages
            set @rowend = @rowstart + ( @pagesize * @maxpagelookahead ) - 1;

            -- Create saved select across items for row numbers
            with ITEMS_SELECT AS
             (    select I.ItemID,
                    ROW_NUMBER() OVER (order by case when @sort=10 THEN isnull(SortDate,9223372036854775807)  end ASC,
                                                case when @sort=11 THEN isnull(SortDate,-1) end DESC) as RowNumber
                    from #TEMP_ITEMS I
                    group by I.ItemID, SortDate )

            -- Insert the correct rows into the temp item table
            insert into @TEMP_PAGED_ITEMS ( ItemID, RowNumber )
            select ItemID, RowNumber
            from ITEMS_SELECT
            where RowNumber >= @rowstart
              and RowNumber <= @rowend;

            -- Return the title information for this page
            select RowNumber as TitleID, G.BibID, G.GroupTitle, G.ALEPH_Number as OPAC_Number, G.OCLC_Number
            , isnull(G.GroupThumbnail,'') as GroupThumbnail, G.[Type], isnull(G.Primary_Identifier_Type,'') as Primary_Identifier_Type
            , isnull(G.Primary_Identifier, '') as Primary_Identifier
            from @TEMP_PAGED_ITEMS T, SobekCM_Item I, SobekCM_Item_Group G
            where ( T.ItemID = I.ItemID )
              and ( I.GroupID = G.GroupID )
            order by RowNumber ASC;

            -- Return the basic system required item information for this page of results
            select T.RowNumber as fk_TitleID, I.ItemID, VID, Title, IP_Restriction_Mask, coalesce(I.MainThumbnail,'') as MainThumbnail
            , coalesce(I.Level1_Index, -1) as Level1_Index, coalesce(I.Level1_Text,'') as Level1_Text
            , coalesce(I.Level2_Index, -1) as Level2_Index, coalesce(I.Level2_Text,'') as Level2_Text
            , coalesce(I.Level3_Index,-1) as Level3_Index, coalesce(I.Level3_Text,'') as Level3_Text
            , isnull(I.PubDate,'') as PubDate, I.[PageCount], coalesce(I.Link,'') as Link
            , coalesce( Spatial_KML, '') as Spatial_KML, coalesce(COinS_OpenURL, '') as COinS_OpenURL
            from SobekCM_Item I, @TEMP_PAGED_ITEMS T
            where ( T.ItemID = I.ItemID )
            order by T.RowNumber, Level1_Index, Level2_Index, Level3_Index;

            -- Return the aggregation-specific display values for all the items in this page of results
            execute sp_Executesql @item_display_sql, N' @itemtable TempPagedItemsTableType READONLY', @TEMP_PAGED_ITEMS;
        end

        -- Return the facets if asked for
        if ( @include_facets = 'true' )
        begin
            -- Build the aggregation list
            if ( LEN( isnull( @aggregationcode, '')) = 0 )
            begin
                select A.Code, A.ShortName, Metadata_Count=Count(*)
                from SobekCM_Item_Aggregation A, SobekCM_Item_Aggregation_Item_Link L, SobekCM_Item I, #TEMP_ITEMS T
                where ( T.ItemID = I.ItemID )
                  and ( I.ItemID = L.ItemID )
                  and ( L.AggregationID = A.AggregationID )
                  and ( A.Hidden = 'false' )
                  and ( A.isActive = 'true' )
                  and ( A.Include_In_Collection_Facet = 'true' )
                group by A.Code, A.ShortName
                order by Metadata_Count DESC, ShortName ASC;
            end;

            -- Return the FIRST facet
            if ( @facettype1 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype1 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end;

            -- Return the SECOND facet
            if ( @facettype2 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype2 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end;

            -- Return the THIRD facet
            if ( @facettype3 > 0 )
            begin
                -- Return the first 100 values
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype3 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end;

            -- Return the FOURTH facet
            if ( @facettype4 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype4 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end;

            -- Return the FIFTH facet
            if ( @facettype5 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype5 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end

            -- Return the SIXTH facet
            if ( @facettype6 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)
                        where ( U.ItemID = I.ItemID )
                          and ( U.MetadataTypeID = @facettype6 )
                        group by U.MetadataID
                        order by Metadata_Count DESC ) F, SobekCM_Metadata_Unique_Search_Table M
                where M.MetadataID = F.MetadataID
                order by Metadata_Count DESC, MetadataValue ASC;
            end;

            -- Return the SEVENTH facet
            if ( @facettype7 > 0 )
            begin
                -- Return the first 100 values
                select MetadataValue, Metadata_Count
                from (    select top(100) U.MetadataID, Metadata_Count = COUNT(*)
                        from #TEMP_ITEMS I, Metadata_Item_Link_Indexed_View U with (NOEXPAND)

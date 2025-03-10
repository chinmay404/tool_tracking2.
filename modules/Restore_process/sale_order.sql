PGDMP  	    &                |            backup_tool_tracking "   14.11 (Ubuntu 14.11-1.pgdg22.04+1)     16.2 (Ubuntu 16.2-1.pgdg22.04+1)     r           0    0    ENCODING    ENCODING        SET client_encoding = 'UTF8';
                      false            s           0    0 
   STDSTRINGS 
   STDSTRINGS     (   SET standard_conforming_strings = 'on';
                      false            t           0    0 
   SEARCHPATH 
   SEARCHPATH     8   SELECT pg_catalog.set_config('search_path', '', false);
                      false            u           1262    59205    backup_tool_tracking    DATABASE     z   CREATE DATABASE backup_tool_tracking WITH TEMPLATE = template0 ENCODING = 'UTF8' LOCALE_PROVIDER = libc LOCALE = 'en_IN';
 $   DROP DATABASE backup_tool_tracking;
                postgres    false            �            1259    59294    outlet_saleorder    TABLE     4  CREATE TABLE public.outlet_saleorder (
    status character varying(20) NOT NULL,
    grn_number character varying(50) NOT NULL,
    po_number character varying(50) NOT NULL,
    bill_no character varying(50) NOT NULL,
    vehicle_no character varying(20),
    uuids jsonb,
    group_id_id integer,
    destination character varying(200),
    driver_name character varying(200),
    checked boolean NOT NULL,
    checked_by_id bigint,
    verified boolean NOT NULL,
    verified_by_id bigint,
    unit_id character varying(100),
    unit character varying(100)
);
 $   DROP TABLE public.outlet_saleorder;
       public         heap    postgres    false            o          0    59294    outlet_saleorder 
   TABLE DATA           �   COPY public.outlet_saleorder (status, grn_number, po_number, bill_no, vehicle_no, uuids, group_id_id, destination, driver_name, checked, checked_by_id, verified, verified_by_id, unit_id, unit) FROM stdin;
    public          postgres    false    235   n       �           2606    59403 &   outlet_saleorder outlet_saleorder_pkey 
   CONSTRAINT     i   ALTER TABLE ONLY public.outlet_saleorder
    ADD CONSTRAINT outlet_saleorder_pkey PRIMARY KEY (bill_no);
 P   ALTER TABLE ONLY public.outlet_saleorder DROP CONSTRAINT outlet_saleorder_pkey;
       public            postgres    false    235            �           1259    59448 &   outlet_saleorder_bill_no_a1daf25c_like    INDEX     z   CREATE INDEX outlet_saleorder_bill_no_a1daf25c_like ON public.outlet_saleorder USING btree (bill_no varchar_pattern_ops);
 :   DROP INDEX public.outlet_saleorder_bill_no_a1daf25c_like;
       public            postgres    false    235            �           1259    59449 '   outlet_saleorder_checked_by_id_3ea23f6f    INDEX     m   CREATE INDEX outlet_saleorder_checked_by_id_3ea23f6f ON public.outlet_saleorder USING btree (checked_by_id);
 ;   DROP INDEX public.outlet_saleorder_checked_by_id_3ea23f6f;
       public            postgres    false    235            �           1259    59450 %   outlet_saleorder_group_id_id_13e83b6d    INDEX     i   CREATE INDEX outlet_saleorder_group_id_id_13e83b6d ON public.outlet_saleorder USING btree (group_id_id);
 9   DROP INDEX public.outlet_saleorder_group_id_id_13e83b6d;
       public            postgres    false    235            �           1259    59451 !   outlet_saleorder_unit_id_292a4125    INDEX     a   CREATE INDEX outlet_saleorder_unit_id_292a4125 ON public.outlet_saleorder USING btree (unit_id);
 5   DROP INDEX public.outlet_saleorder_unit_id_292a4125;
       public            postgres    false    235            �           1259    59452 &   outlet_saleorder_unit_id_292a4125_like    INDEX     z   CREATE INDEX outlet_saleorder_unit_id_292a4125_like ON public.outlet_saleorder USING btree (unit_id varchar_pattern_ops);
 :   DROP INDEX public.outlet_saleorder_unit_id_292a4125_like;
       public            postgres    false    235            �           1259    59453 (   outlet_saleorder_verified_by_id_908add0a    INDEX     o   CREATE INDEX outlet_saleorder_verified_by_id_908add0a ON public.outlet_saleorder USING btree (verified_by_id);
 <   DROP INDEX public.outlet_saleorder_verified_by_id_908add0a;
       public            postgres    false    235            �           2606    59550 E   outlet_saleorder outlet_saleorder_checked_by_id_3ea23f6f_fk_managment    FK CONSTRAINT     �   ALTER TABLE ONLY public.outlet_saleorder
    ADD CONSTRAINT outlet_saleorder_checked_by_id_3ea23f6f_fk_managment FOREIGN KEY (checked_by_id) REFERENCES public.managment_customuser(id) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.outlet_saleorder DROP CONSTRAINT outlet_saleorder_checked_by_id_3ea23f6f_fk_managment;
       public          postgres    false    235            �           2606    59555 C   outlet_saleorder outlet_saleorder_group_id_id_13e83b6d_fk_outlet_sa    FK CONSTRAINT     �   ALTER TABLE ONLY public.outlet_saleorder
    ADD CONSTRAINT outlet_saleorder_group_id_id_13e83b6d_fk_outlet_sa FOREIGN KEY (group_id_id) REFERENCES public.outlet_saleordergroup(group_id) DEFERRABLE INITIALLY DEFERRED;
 m   ALTER TABLE ONLY public.outlet_saleorder DROP CONSTRAINT outlet_saleorder_group_id_id_13e83b6d_fk_outlet_sa;
       public          postgres    false    235            �           2606    59560 E   outlet_saleorder outlet_saleorder_unit_id_292a4125_fk_units_unit_name    FK CONSTRAINT     �   ALTER TABLE ONLY public.outlet_saleorder
    ADD CONSTRAINT outlet_saleorder_unit_id_292a4125_fk_units_unit_name FOREIGN KEY (unit_id) REFERENCES public.units_unit(name) DEFERRABLE INITIALLY DEFERRED;
 o   ALTER TABLE ONLY public.outlet_saleorder DROP CONSTRAINT outlet_saleorder_unit_id_292a4125_fk_units_unit_name;
       public          postgres    false    235            �           2606    59565 F   outlet_saleorder outlet_saleorder_verified_by_id_908add0a_fk_managment    FK CONSTRAINT     �   ALTER TABLE ONLY public.outlet_saleorder
    ADD CONSTRAINT outlet_saleorder_verified_by_id_908add0a_fk_managment FOREIGN KEY (verified_by_id) REFERENCES public.managment_customuser(id) DEFERRABLE INITIALLY DEFERRED;
 p   ALTER TABLE ONLY public.outlet_saleorder DROP CONSTRAINT outlet_saleorder_verified_by_id_908add0a_fk_managment;
       public          postgres    false    235            o   �   x��νjC1���)B��򏬗萎M[��@�����6����A�����R��oCIGN�'�(b�������-ZW��@�)���@BW��":r5�߾m^���_��g��?��f��c_��|=�{[]aUѿ)�*��GՒAJ ���[�I��t�z���Ж���|�R�����K�ڒ��=v�Z�:z��������_����T~     
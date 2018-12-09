from cis_interface.metaschema.datatypes import (
    get_type_class, complete_typedef, encode_data)
from cis_interface.metaschema.datatypes.MetaschemaType import MetaschemaType


class ContainerMetaschemaType(MetaschemaType):
    r"""Type associated with a container of subtypes."""

    name = 'container'
    description = 'A container of other types.'
    python_types = []

    _container_type = None
    _json_type = None
    _json_property = None

    def __init__(self, *args, **kwargs):
        self._typecls = self._container_type()
        super(ContainerMetaschemaType, self).__init__(*args, **kwargs)

    @classmethod
    def _iterate(cls, container):
        r"""Iterate over the contents of the container. Each element returned
        should be a tuple including an index and a value.

        Args:
            container (obj): Object to be iterated over.

        Returns:
            iterator: Iterator over elements in the container.

        """
        raise NotImplementedError("This must be overwritten by the subclass.")

    @classmethod
    def _assign(cls, container, index, value):
        r"""Assign an element in the container to the specified value.

        Args:
            container (obj): Object that element will be assigned to.
            index (obj): Index in the container object where element will be
                assigned.
            value (obj): Value that will be assigned to the element in the
                container object.

        """
        raise NotImplementedError("This must be overwritten by the subclass.")

    @classmethod
    def _has_element(cls, container, index):
        r"""Check to see if an index is in the container.

        Args:
            container (obj): Object that should be checked for index.
            index (obj): Index that should be checked for.

        Returns:
            bool: True if the index is in the container.

        """
        raise NotImplementedError("This must be overwritten by the subclass.")

    @classmethod
    def _get_element(cls, container, index, default):
        r"""Get an element from the container if it exists, otherwise return
        the default.

        Args:
            container (obj): Object that should be returned from.
            index (obj): Index of element that should be returned.
            default (obj): Default that should be returned if the index is not
                in the container.

        Returns:
            object: Container contents at specified element.

        """
        out = default
        if cls._has_element(container, index):
            out = container[index]
        return out

    @classmethod
    def encode_data(cls, obj, typedef):
        r"""Encode an object's data.

        Args:
            obj (object): Object to encode.
            typedef (dict): Type definition that should be used to encode the
                object.

        Returns:
            string: Encoded object.

        """
        container = cls._container_type()
        for k, v in cls._iterate(obj):
            if cls._json_property in typedef:
                vtypedef = cls._get_element(typedef[cls._json_property], k, None)
            else:
                vtypedef = None
            vbytes = encode_data(v, typedef=vtypedef)
            cls._assign(container, k, vbytes)
        return container

    @classmethod
    def decode_data(cls, obj, typedef):
        r"""Decode an object.

        Args:
            obj (string): Encoded object to decode.
            typedef (dict): Type definition that should be used to decode the
                object.

        Returns:
            object: Decoded object.

        """
        container = cls._container_type()
        for k, v in cls._iterate(obj):
            vtypedef = cls._get_element(typedef[cls._json_property], k, {})
            vcls = get_type_class(vtypedef['type'])
            cls._assign(container, k, vcls.decode_data(v, vtypedef))
        return container

    @classmethod
    def transform_type(cls, obj, typedef=None):
        r"""Transform an object based on type info.

        Args:
            obj (object): Object to transform.
            typedef (dict, optional): Type definition that should be used to
                transform the object. Defaults to None and no transformation
                is performed.

        Returns:
            object: Transformed object.

        """
        if typedef is None:
            return obj
        # if cls._json_property in typedef:
        #     for k, v in cls._iterate(obj):
        #         if cls._has_element(typedef[cls._json_property], k):
        #             vtype = cls._get_element(typedef[cls._json_property], k, None)
        #             vcls = get_type_class(vtype['type'])  # required
        #             cls._assign(obj, k, vcls.transform_type(obj[k], typedef=vtype))
        return obj

    @classmethod
    def extract_typedef(cls, metadata):
        r"""Extract the minimum typedef required for this type from the provided
        metadata.

        Args:
            metadata (dict): Message metadata.

        Returns:
            dict: Encoded type definition with unncessary properties removed.

        """
        out = super(ContainerMetaschemaType, cls).extract_typedef(metadata)
        # if cls._json_property in out:
        #     contents = out[cls._json_property]
        #     if isinstance(contents, cls.python_types):
        #         for k, v in cls._iterate(contents):
        #             if 'type' in v:
        #                 vcls = get_type_class(v['type'])
        #                 cls._assign(contents, k, vcls.extract_typedef(v))
        #         out[cls._json_property] = contents
        return out

    def update_typedef(self, **kwargs):
        r"""Update the current typedef with new values.

        Args:
            **kwargs: All keyword arguments are considered to be new type
                definitions. If they are a valid definition property, they
                will be copied to the typedef associated with the instance.

        Returns:
            dict: A dictionary of keyword arguments that were not added to the
                type definition.

        """
        map = kwargs.get(self._json_property, None)
        map_out = self._container_type()
        if isinstance(map, self.python_types):
            for k, v in self._iterate(map):
                v_typedef = complete_typedef(v)
                if self._has_element(self._typecls, k):
                    self._assign(map_out, k,
                                 self._typecls[k].update_typedef(**v_typedef))
                else:
                    self._assign(self._typecls, k,
                                 get_type_class(v_typedef['type'])(**v_typedef))
                self._assign(map, k, self._typecls[k]._typedef)
            kwargs[self._json_property] = map
        out = super(ContainerMetaschemaType, self).update_typedef(**kwargs)
        if map_out:
            out[self._json_property] = map_out
        return out
